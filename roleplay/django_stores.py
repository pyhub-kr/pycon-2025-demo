"""
Django-specific chat history storage implementation.
"""

from typing import Optional
from .core import Message, BaseChatConfig, SimpleChatConfig, BaseChatHistoryStore, UsageInfo


class DjangoChatHistoryStore(BaseChatHistoryStore):
    """단순한 Django 채팅 히스토리 스토어"""
    
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
            from .models import ChatSession
            
            if self.session_id:
                # 기존 세션 로드
                self._session = ChatSession.objects.get(pk=self.session_id)
            else:
                # 새 세션 생성
                if not self.config:
                    raise ValueError("Config is required to create a new session")
                
                # SimpleChatConfig에서 instruction 추출
                instruction = ""
                if isinstance(self.config, SimpleChatConfig):
                    instruction = self.config.instruction
                elif hasattr(self.config, 'build_system_prompt'):
                    instruction = self.config.build_system_prompt()
                
                self._session = ChatSession.objects.create(
                    user=self.user,
                    instruction=instruction,
                    model=getattr(self.config, 'model', 'gpt-4o'),
                    temperature=getattr(self.config, 'temperature', 1.0),
                    max_tokens=getattr(self.config, 'max_tokens', 1000),
                )
        
        return self._session
    
    def add_message(self, message: Message) -> None:
        """메시지를 데이터베이스에 추가"""
        from .models import ChatMessage
        
        # 메시지 생성
        chat_message = ChatMessage.objects.create(
            session=self.session,
            role=message.role,
            content=message.content,
        )
        
        # 토큰 정보가 있으면 저장
        if message.usage:
            total_tokens = message.usage.total_tokens if hasattr(message.usage, 'total_tokens') else (
                message.usage.input_tokens + message.usage.output_tokens
            )
            chat_message.token_count = total_tokens
            chat_message.save()
            
            # 세션의 총 토큰 수 업데이트
            self.session.total_tokens += total_tokens
            self.session.save()
    
    def get_messages(self, limit: Optional[int] = None) -> list[Message]:
        """데이터베이스에서 메시지 목록을 가져옴"""
        from .models import ChatMessage
        
        queryset = ChatMessage.objects.filter(session=self.session).order_by("created_at")
        
        if limit is not None:
            # 최근 limit개 메시지만 가져오기
            queryset = queryset[max(0, queryset.count() - limit):]
        
        return [
            Message(role=msg.role, content=msg.content, created_at=msg.created_at) 
            for msg in queryset
        ]
    
    def clear_history(self) -> None:
        """해당 세션의 모든 메시지를 삭제"""
        from .models import ChatMessage
        
        ChatMessage.objects.filter(session=self.session).delete()
    
    def get_message_count(self) -> int:
        """세션의 총 메시지 수 반환"""
        from .models import ChatMessage
        
        return ChatMessage.objects.filter(session=self.session).count()


def create_django_chat_store(request, config: BaseChatConfig, session_id: Optional[int] = None) -> DjangoChatHistoryStore:
    """
    Django request 객체로부터 DjangoChatHistoryStore를 생성하는 헬퍼 함수
    
    Args:
        request: Django HttpRequest 객체
        config: BaseChatConfig 객체 (주로 SimpleChatConfig)
        session_id: 기존 세션 ID (선택사항)
    
    Returns:
        DjangoChatHistoryStore 인스턴스
    """
    user = request.user if request.user.is_authenticated else None
    return DjangoChatHistoryStore(session_id=session_id, config=config, user=user)