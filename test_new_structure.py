"""
간소화된 채팅 세션 구조 테스트
"""

import os
import django

# Django 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from roleplay.core import SimpleChatConfig, ChatService
from roleplay.django_stores import DjangoChatHistoryStore
from roleplay.models import ChatSession, ChatMessage
from django.contrib.auth.models import User


def test_simple_chat():
    """간단한 채팅 세션 테스트"""
    print("\n=== 간단한 채팅 세션 테스트 ===")

    # SimpleChatConfig 생성
    config = SimpleChatConfig(instruction="You are a helpful assistant. Be concise and friendly.")

    # DjangoChatHistoryStore 생성
    store = DjangoChatHistoryStore(config=config)

    # ChatService 생성
    service = ChatService(
        config=config, chat_history_store=store, model="gpt-4o", temperature=0.7, max_tokens=500, verbose=True
    )

    # 첫 번째 메시지 전송
    response1 = service.send("안녕하세요! 파이썬 프로그래밍에 대해 알고 싶어요.")
    print(f"\nAI 응답: {response1.text}")
    print(f"추천 표현: {response1.suggested_phrases[:3]}")

    # 두 번째 메시지 전송 (대화 이어가기)
    response2 = service.send("파이썬의 주요 특징은 무엇인가요?")
    print(f"\nAI 응답: {response2.text}")

    # 세션 정보 확인
    session = store.session
    print(f"\n세션 정보:")
    print(f"- ID: {session.id}")
    print(f"- Title: {session.title or 'Untitled'}")
    print(f"- Model: {session.model}")
    print(f"- Temperature: {session.temperature}")
    print(f"- Max Tokens: {session.max_tokens}")
    print(f"- Instruction (첫 50자): {session.instruction[:50]}...")

    # 메시지 확인
    messages = store.get_messages()
    print(f"\n저장된 메시지 수: {len(messages)}")
    for i, msg in enumerate(messages, 1):
        print(f"  {i}. {msg.role}: {msg.content[:50]}...")

    return session.id


def test_existing_session(session_id):
    """기존 세션 재사용 테스트"""
    print(f"\n=== 기존 세션 재사용 테스트 (Session ID: {session_id}) ===")

    # 기존 세션을 사용하는 store 생성
    store = DjangoChatHistoryStore(session_id=session_id)

    # 세션에서 설정 정보 복원
    session = store.session
    config = SimpleChatConfig(instruction=session.instruction)

    # ChatService 생성
    service = ChatService(
        config=config,
        chat_history_store=store,
        model=session.model,
        temperature=session.temperature,
        max_tokens=session.max_tokens,
        verbose=False,
    )

    # 이전 대화 이어가기
    response = service.send("방금 설명한 내용을 요약해주세요.")
    print(f"\nAI 응답: {response.text}")

    # 전체 메시지 수 확인
    total_messages = store.get_message_count()
    print(f"\n전체 메시지 수: {total_messages}")


def test_database_queries():
    """데이터베이스 직접 쿼리 테스트"""
    print("\n=== 데이터베이스 쿼리 테스트 ===")

    # 모든 세션 조회
    sessions = ChatSession.objects.all()
    print(f"\n총 세션 수: {sessions.count()}")

    for session in sessions:
        print(f"\n세션 #{session.id}:")
        print(f"  - 제목: {session.title or 'Untitled'}")
        print(f"  - 활성 상태: {session.is_active}")
        print(f"  - 메시지 수: {session.message_set.count()}")

        # 해당 세션의 메시지들
        messages = session.message_set.all()[:3]  # 처음 3개만
        for msg in messages:
            print(f"    • {msg.role}: {msg.content[:30]}...")

    # 전체 메시지 통계
    total_messages = ChatMessage.objects.count()
    user_messages = ChatMessage.objects.filter(role="user").count()
    assistant_messages = ChatMessage.objects.filter(role="assistant").count()

    print(f"\n메시지 통계:")
    print(f"  - 전체: {total_messages}")
    print(f"  - User: {user_messages}")
    print(f"  - Assistant: {assistant_messages}")


def main():
    """메인 테스트 함수"""
    try:
        # 1. 새 세션으로 채팅 테스트
        session_id = test_simple_chat()

        # 2. 기존 세션 재사용 테스트
        test_existing_session(session_id)

        # 3. 데이터베이스 쿼리 테스트
        test_database_queries()

        print("\n✅ 모든 테스트가 성공적으로 완료되었습니다!")

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
