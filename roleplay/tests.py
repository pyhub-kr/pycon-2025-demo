from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models import RolePlaySession, ChatMessage
from .core import UsageInfo


class RolePlaySessionModelTest(TestCase):
    """RolePlaySession 모델 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.user = User.objects.create_user(username="testuser", password="testpassword")

    def test_create_session(self):
        """세션 생성 테스트"""
        session = RolePlaySession.objects.create(
            user=self.user,
            prompt_name="restaurant",
            language="한국어",
            user_role="손님",
            gpt_role="웨이터",
            difficulty=RolePlaySession.DifficultyChoices.BEGINNER,
        )

        self.assertEqual(session.prompt_name, "restaurant")
        self.assertEqual(session.language, "한국어")
        self.assertEqual(session.difficulty, "beginner")
        self.assertEqual(session.input_tokens, 0)
        self.assertEqual(session.output_tokens, 0)

    def test_session_without_user(self):
        """로그인하지 않은 사용자의 세션 생성 테스트"""
        session = RolePlaySession.objects.create(
            prompt_name="starbucks",
            language="English",
            user_role="customer",
            gpt_role="barista",
            difficulty=RolePlaySession.DifficultyChoices.INTERMEDIATE,
        )

        self.assertIsNone(session.user)
        self.assertEqual(session.difficulty, "intermediate")

    def test_difficulty_choices(self):
        """난이도 선택지 테스트"""
        choices = RolePlaySession.DifficultyChoices

        self.assertEqual(choices.BEGINNER.value, "beginner")
        self.assertEqual(choices.BEGINNER.label, "Beginner")
        self.assertEqual(choices.INTERMEDIATE.value, "intermediate")
        self.assertEqual(choices.ADVANCED.value, "advanced")

    def test_session_str_method(self):
        """__str__ 메서드 테스트"""
        session = RolePlaySession.objects.create(
            prompt_name="cafe", language="한국어", user_role="손님", gpt_role="직원"
        )

        expected = f"cafe - 한국어 (ID: {session.id})"
        self.assertEqual(str(session), expected)

    def test_token_usage_tracking(self):
        """토큰 사용량 추적 테스트"""
        session = RolePlaySession.objects.create(
            prompt_name="restaurant", language="한국어", user_role="손님", gpt_role="웨이터"
        )

        # 토큰 사용량 업데이트
        session.input_tokens = 100
        session.output_tokens = 150
        session.save()

        # 데이터베이스에서 다시 조회
        updated_session = RolePlaySession.objects.get(pk=session.pk)
        self.assertEqual(updated_session.input_tokens, 100)
        self.assertEqual(updated_session.output_tokens, 150)


class ChatMessageModelTest(TestCase):
    """ChatMessage 모델 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.session = RolePlaySession.objects.create(
            prompt_name="restaurant", language="한국어", user_role="손님", gpt_role="웨이터"
        )

    def test_create_user_message(self):
        """사용자 메시지 생성 테스트"""
        message = ChatMessage.objects.create(
            session=self.session, role=ChatMessage.RoleChoices.USER, content="안녕하세요, 메뉴판 좀 보여주세요."
        )

        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "안녕하세요, 메뉴판 좀 보여주세요.")
        self.assertIsNotNone(message.created_at)
        self.assertIsNone(message.input_tokens)

    def test_create_assistant_message_with_usage(self):
        """어시스턴트 메시지와 사용량 정보 생성 테스트"""
        message = ChatMessage.objects.create(
            session=self.session,
            role=ChatMessage.RoleChoices.ASSISTANT,
            content="안녕하세요! 메뉴판을 보여드리겠습니다.",
            input_tokens=50,
            output_tokens=30,
        )

        self.assertEqual(message.role, "assistant")
        self.assertEqual(message.input_tokens, 50)
        self.assertEqual(message.output_tokens, 30)

    def test_role_choices(self):
        """역할 선택지 테스트"""
        choices = ChatMessage.RoleChoices

        self.assertEqual(choices.USER.value, "user")
        self.assertEqual(choices.USER.label, "User")
        self.assertEqual(choices.ASSISTANT.value, "assistant")
        self.assertEqual(choices.SYSTEM.value, "system")

    def test_message_str_method(self):
        """__str__ 메서드 테스트"""
        # 짧은 메시지
        short_msg = ChatMessage.objects.create(
            session=self.session, role=ChatMessage.RoleChoices.USER, content="짧은 메시지"
        )
        self.assertEqual(str(short_msg), "user: 짧은 메시지")

        # 긴 메시지
        long_content = "아" * 60  # 60자
        long_msg = ChatMessage.objects.create(
            session=self.session, role=ChatMessage.RoleChoices.ASSISTANT, content=long_content
        )
        expected = f"assistant: {'아' * 50}..."
        self.assertEqual(str(long_msg), expected)

    def test_message_ordering(self):
        """메시지 정렬 테스트"""
        # 여러 메시지 생성
        msg1 = ChatMessage.objects.create(session=self.session, role=ChatMessage.RoleChoices.USER, content="첫 번째")
        msg2 = ChatMessage.objects.create(
            session=self.session, role=ChatMessage.RoleChoices.ASSISTANT, content="두 번째"
        )
        msg3 = ChatMessage.objects.create(session=self.session, role=ChatMessage.RoleChoices.USER, content="세 번째")

        # 정렬 확인
        messages = list(ChatMessage.objects.filter(session=self.session))
        self.assertEqual(messages[0].content, "첫 번째")
        self.assertEqual(messages[1].content, "두 번째")
        self.assertEqual(messages[2].content, "세 번째")

    def test_session_messages_relationship(self):
        """세션과 메시지의 관계 테스트"""
        # 메시지 생성
        ChatMessage.objects.create(session=self.session, role=ChatMessage.RoleChoices.USER, content="테스트 1")
        ChatMessage.objects.create(session=self.session, role=ChatMessage.RoleChoices.ASSISTANT, content="테스트 2")

        # related_name으로 접근
        messages = self.session.message_set.all()
        self.assertEqual(messages.count(), 2)

        # 세션 삭제 시 메시지도 삭제되는지 확인
        session_id = self.session.id
        self.session.delete()

        remaining_messages = ChatMessage.objects.filter(session_id=session_id)
        self.assertEqual(remaining_messages.count(), 0)


class ModelIntegrationTest(TestCase):
    """모델 간 통합 테스트"""

    def test_full_conversation_flow(self):
        """전체 대화 흐름 테스트"""
        # 세션 생성
        session = RolePlaySession.objects.create(
            prompt_name="restaurant",
            language="한국어",
            user_role="손님",
            gpt_role="웨이터",
            difficulty=RolePlaySession.DifficultyChoices.INTERMEDIATE,
        )

        # 대화 진행
        user_msg = ChatMessage.objects.create(
            session=session, role=ChatMessage.RoleChoices.USER, content="메뉴 추천해주세요"
        )

        assistant_msg = ChatMessage.objects.create(
            session=session,
            role=ChatMessage.RoleChoices.ASSISTANT,
            content="오늘의 특선 요리로 스테이크를 추천드립니다.",
            input_tokens=100,
            output_tokens=50,
        )

        # 세션의 토큰 사용량 업데이트
        session.input_tokens += assistant_msg.input_tokens
        session.output_tokens += assistant_msg.output_tokens
        session.save()

        # 검증
        self.assertEqual(session.message_set.count(), 2)
        self.assertEqual(session.input_tokens + session.output_tokens, 150)

        # 대화 이어가기
        ChatMessage.objects.create(session=session, role=ChatMessage.RoleChoices.USER, content="가격은 얼마인가요?")

        ChatMessage.objects.create(
            session=session,
            role=ChatMessage.RoleChoices.ASSISTANT,
            content="스테이크는 35,000원입니다.",
            input_tokens=120,
            output_tokens=30,
        )

        # 최종 메시지 수 확인
        self.assertEqual(session.message_set.count(), 4)

    def test_session_ordering(self):
        """세션 정렬 테스트"""
        # 여러 세션 생성
        session1 = RolePlaySession.objects.create(
            prompt_name="cafe", language="한국어", user_role="손님", gpt_role="직원"
        )
        session2 = RolePlaySession.objects.create(
            prompt_name="restaurant", language="한국어", user_role="손님", gpt_role="웨이터"
        )

        # 가장 최근에 업데이트된 순서로 정렬되는지 확인
        sessions = list(RolePlaySession.objects.all())
        self.assertEqual(sessions[0].id, session2.id)  # 가장 최근에 생성된 것이 먼저
        self.assertEqual(sessions[1].id, session1.id)
