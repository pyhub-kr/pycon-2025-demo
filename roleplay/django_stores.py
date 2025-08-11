"""
Django-specific chat history storage implementation.
"""

from typing import Optional
from roleplay.core import Message, BaseChatHistoryStore
from roleplay.models import ChatSession


class DjangoChatHistoryStore(BaseChatHistoryStore):
    """단순한 Django 채팅 히스토리 스토어"""

    def __init__(self, session: ChatSession):
        """
        Django 모델을 사용한 채팅 기록 저장소 초기화

        Args:
            session: ChatSession 객체 (필수)
        """
        self.session = session

    def add_message(self, message: Message) -> None:
        """메시지를 데이터베이스에 추가"""

        # 메시지 생성
        self.session.message_set.create(
            role=message.role,
            content=message.content,
        )

    def get_messages(self, limit: Optional[int] = None) -> list[Message]:
        """데이터베이스에서 메시지 목록을 가져옴"""

        queryset = self.session.message_set.all()

        if limit:
            queryset = reversed(queryset.order_by("-id")[:limit])
        else:
            queryset = queryset.order_by("id")

        return [
            Message(role=chat_message.role, content=chat_message.content, created_at=chat_message.created_at)
            for chat_message in queryset
        ]

    def clear_history(self) -> None:
        """해당 세션의 모든 메시지를 삭제"""

        self.session.message_set.all().delete()

    def get_message_count(self) -> int:
        """세션의 총 메시지 수 반환"""

        return self.session.message_set.all().count()
