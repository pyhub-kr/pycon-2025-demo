"""
Django-specific chat history storage implementations.
"""

from abc import abstractmethod
from typing import Optional

from django.contrib.contenttypes.models import ContentType

from roleplay.core import Message, BaseChatConfig, RolePlayChatConfig, SimpleChatConfig, BaseChatHistoryStore


class BaseDjangoChatHistoryStore(BaseChatHistoryStore):
    """Django 기반 채팅 히스토리 스토어의 추상 기본 클래스"""

    session_model = None  # 서브클래스에서 정의

    def __init__(self, session_id: Optional[int] = None, config: Optional[BaseChatConfig] = None, user=None):
        """
        Django 모델을 사용한 채팅 기록 저장소 초기화

        Args:
            session_id: 기존 세션 ID (선택사항)
            config: 채팅 설정 (새 세션 생성 시 필요)
            user: Django User 객체 (선택사항)
        """
        self.session_id = session_id
        self.config = config
        self.user = user
        self._session = None

    @property
    def session(self):
        """세션 객체를 lazy loading으로 가져오거나 생성"""
        if self._session is None:
            if self.session_id:
                # 기존 세션 로드
                self._session = self.session_model.objects.get(pk=self.session_id)
            else:
                # 새 세션 생성
                if not self.config:
                    raise ValueError("Config is required to create a new session")
                self._session = self.create_session()
        return self._session

    @abstractmethod
    def create_session(self):
        """서브클래스에서 세션 생성 로직 구현"""
        pass

    def add_message(self, message: Message) -> None:
        """메시지를 데이터베이스에 추가"""
        from .models import ChatMessage

        # ContentType 가져오기
        content_type = ContentType.objects.get_for_model(self.session)

        # 메시지 생성
        chat_message = ChatMessage.objects.create(
            content_type=content_type,
            object_id=self.session.pk,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )

        # Assistant 메시지인 경우 사용량 정보 저장
        if message.role == "assistant" and message.usage:
            chat_message.input_tokens = message.usage.input_tokens
            chat_message.output_tokens = message.usage.output_tokens
            chat_message.save()

            # 세션의 총 사용량 업데이트
            self.session.input_tokens += message.usage.input_tokens
            self.session.output_tokens += message.usage.output_tokens
            self.session.save()

    def get_messages(self, limit: Optional[int] = None) -> list[Message]:
        """데이터베이스에서 메시지 목록을 가져옴"""
        from .models import ChatMessage

        content_type = ContentType.objects.get_for_model(self.session)
        queryset = ChatMessage.objects.filter(content_type=content_type, object_id=self.session.pk).order_by("id")

        if limit is not None:
            # 최근 limit개 메시지만 가져오기
            queryset = queryset[max(0, queryset.count() - limit) :]

        return [Message(role=msg.role, content=msg.content, created_at=msg.created_at) for msg in queryset]

    def clear_history(self) -> None:
        """해당 세션의 모든 메시지를 삭제"""
        from .models import ChatMessage

        content_type = ContentType.objects.get_for_model(self.session)
        ChatMessage.objects.filter(content_type=content_type, object_id=self.session.pk).delete()

    def get_message_count(self) -> int:
        """세션의 총 메시지 수 반환"""
        from .models import ChatMessage

        content_type = ContentType.objects.get_for_model(self.session)
        return ChatMessage.objects.filter(content_type=content_type, object_id=self.session.pk).count()

    def deactivate_session(self) -> None:
        """세션을 비활성화"""
        if hasattr(self.session, "is_active"):
            self.session.is_active = False
            self.session.save()


class GeneralDjangoChatHistoryStore(BaseDjangoChatHistoryStore):
    """일반 채팅용 스토어"""

    def __init__(self, session_id: Optional[int] = None, config: Optional[BaseChatConfig] = None, user=None):
        super().__init__(session_id, config, user)
        # Lazy import to avoid circular dependency
        from .models import GeneralChatSession

        self.session_model = GeneralChatSession

    def create_session(self):
        """일반 채팅 세션 생성"""
        # 설정에서 정보 추출
        title = getattr(self.config, "title", "")
        purpose = getattr(self.config, "purpose", "general")
        context = getattr(self.config, "context", "")

        # SimpleChatConfig인 경우 instruction을 context로 사용
        if isinstance(self.config, SimpleChatConfig):
            context = self.config.instruction

        return self.session_model.objects.create(
            user=self.user,
            title=title,
            purpose=purpose,
            context=context,
            system_prompt=self.config.build_system_prompt() if self.config else "",
            model=getattr(self.config, "model", "gpt-4o"),
            temperature=getattr(self.config, "temperature", 1.0),
            max_tokens=getattr(self.config, "max_tokens", 1000),
        )


class RolePlayDjangoChatHistoryStore(BaseDjangoChatHistoryStore):
    """역할극 전용 스토어"""

    def __init__(self, session_id: Optional[int] = None, config: Optional[RolePlayChatConfig] = None, user=None):
        super().__init__(session_id, config, user)
        # Lazy import to avoid circular dependency
        from .models import RolePlayChatSession

        self.session_model = RolePlayChatSession

    def create_session(self):
        """역할극 세션 생성"""
        if not isinstance(self.config, RolePlayChatConfig):
            raise ValueError("RolePlayChatConfig required for roleplay sessions")

        # prompt_name이 config에 없으면 기본값 생성
        prompt_name = getattr(self.config, "prompt_name", f"{self.config.user_role} - {self.config.gpt_role}")

        return self.session_model.objects.create(
            user=self.user,
            prompt_name=prompt_name,
            language=self.config.language,
            user_role=self.config.user_role,
            gpt_role=self.config.gpt_role,
            difficulty=self.config.difficulty.value,
            system_prompt=self.config.build_system_prompt(),
            model=getattr(self.config, "model", "gpt-4o"),
            temperature=getattr(self.config, "temperature", 1.0),
            max_tokens=getattr(self.config, "max_tokens", 1000),
        )


def create_django_chat_store(
    request, config: BaseChatConfig, session_id: Optional[int] = None
) -> BaseDjangoChatHistoryStore:
    """
    Django request 객체로부터 적절한 DjangoChatHistoryStore를 생성하는 헬퍼 함수

    config 타입에 따라 자동으로 적절한 Store 클래스를 선택합니다.

    Args:
        request: Django HttpRequest 객체
        config: BaseChatConfig 객체
        session_id: 기존 세션 ID (선택사항)

    Returns:
        BaseDjangoChatHistoryStore 서브클래스 인스턴스
    """
    user = request.user if request.user.is_authenticated else None

    # config 타입에 따라 적절한 Store 선택
    if isinstance(config, RolePlayChatConfig):
        return RolePlayDjangoChatHistoryStore(session_id=session_id, config=config, user=user)
    elif isinstance(config, SimpleChatConfig):
        return GeneralDjangoChatHistoryStore(session_id=session_id, config=config, user=user)
    else:
        # 기본적으로 일반 채팅 스토어 사용
        return GeneralDjangoChatHistoryStore(session_id=session_id, config=config, user=user)
