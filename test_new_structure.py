"""
새로운 채팅 세션 구조 테스트
"""

import os
import django

# Django 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from roleplay.core import SimpleChatConfig, RolePlayChatConfig, Difficulty, ChatService
from roleplay.django_stores import (
    GeneralDjangoChatHistoryStore,
    RolePlayDjangoChatHistoryStore,
    create_django_chat_store,
)
from roleplay.models import GeneralChatSession, RolePlayChatSession, ChatMessage
from django.contrib.auth.models import User


def test_general_chat():
    """일반 채팅 세션 테스트"""
    print("\n=== 일반 채팅 세션 테스트 ===")

    # SimpleChatConfig 생성
    config = SimpleChatConfig(instruction="You are a helpful assistant for general questions.")

    # GeneralDjangoChatHistoryStore 생성
    store = GeneralDjangoChatHistoryStore(config=config)

    # ChatService 생성
    service = ChatService(config=config, chat_history_store=store, verbose=True)

    # 메시지 전송
    response = service.send("안녕하세요! 오늘 날씨가 어떤가요?")
    print(f"\nAI 응답: {response.text}")

    # 세션 확인
    session = store.session
    print(f"\n세션 정보:")
    print(f"- ID: {session.id}")
    print(f"- Purpose: {session.purpose}")
    print(f"- Model: {session.model}")
    print(f"- Temperature: {session.temperature}")
    print(f"- Total Tokens: {session.total_tokens}")

    # 메시지 확인
    messages = store.get_messages()
    print(f"\n메시지 수: {len(messages)}")

    return session.id


def test_roleplay_chat():
    """역할극 채팅 세션 테스트"""
    print("\n=== 역할극 채팅 세션 테스트 ===")

    # RolePlayChatConfig 생성
    config = RolePlayChatConfig(
        language="English",
        user_role="Tourist visiting Seoul",
        gpt_role="Tour guide in Seoul",
        difficulty=Difficulty.INTERMEDIATE,
        role_template="Help the tourist explore Seoul's attractions.",
    )

    # RolePlayDjangoChatHistoryStore 생성
    store = RolePlayDjangoChatHistoryStore(config=config)

    # ChatService 생성
    service = ChatService(config=config, chat_history_store=store, verbose=True)

    # 메시지 전송
    response = service.send("Where should I visit first in Seoul?")
    print(f"\nAI 응답: {response.text}")
    print(f"추천 표현: {response.suggested_phrases}")

    # 세션 확인
    session = store.session
    print(f"\n세션 정보:")
    print(f"- ID: {session.id}")
    print(f"- Language: {session.language}")
    print(f"- Difficulty: {session.difficulty}")
    print(f"- Model: {session.model}")
    print(f"- Temperature: {session.temperature}")
    print(f"- Total Tokens: {session.total_tokens}")

    return session.id


def test_message_retrieval(general_session_id, roleplay_session_id):
    """메시지 조회 테스트"""
    print("\n=== 메시지 조회 테스트 ===")

    # 일반 세션의 메시지 조회
    general_session = GeneralChatSession.objects.get(id=general_session_id)
    general_messages = ChatMessage.objects.filter(
        content_type__model="generalchatsession", object_id=general_session.id
    )
    print(f"\n일반 세션 메시지 수: {general_messages.count()}")

    # 역할극 세션의 메시지 조회
    roleplay_session = RolePlayChatSession.objects.get(id=roleplay_session_id)
    roleplay_messages = ChatMessage.objects.filter(
        content_type__model="roleplaychatsession", object_id=roleplay_session.id
    )
    print(f"역할극 세션 메시지 수: {roleplay_messages.count()}")

    # 전체 메시지 수
    total_messages = ChatMessage.objects.count()
    print(f"전체 메시지 수: {total_messages}")


def main():
    """메인 테스트 함수"""
    try:
        # 일반 채팅 테스트
        general_session_id = test_general_chat()

        # 역할극 채팅 테스트
        roleplay_session_id = test_roleplay_chat()

        # 메시지 조회 테스트
        test_message_retrieval(general_session_id, roleplay_session_id)

        print("\n✅ 모든 테스트가 성공적으로 완료되었습니다!")

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
