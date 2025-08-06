#!/usr/bin/env python
"""
Django 의존성 없이 RolePlay 테스트 스크립트
"""
import os
import sys
from pathlib import Path

# 프로젝트 경로를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from roleplay.core import (
    ChatService,
    RolePlayChatConfig,
    Difficulty,
    Message,
    ChatResponse,
    InMemoryStore,
)
from roleplay.prompts import STARBUCKS_PROMPT


def test_non_streaming():
    """일반 응답 모드 테스트"""
    print("=" * 50)
    print("일반 응답 모드 테스트")
    print("=" * 50)

    # 설정
    config = RolePlayChatConfig(
        language="한국어",
        user_role="손님",
        gpt_role="웨이터",
        difficulty=Difficulty.BEGINNER,
        role_template=STARBUCKS_PROMPT,
    )

    # 채팅 기록 저장소 (메모리 기반)
    chat_store = InMemoryStore()

    # 서비스 생성
    service = ChatService(config=config, chat_history_store=chat_store, temperature=0.8, max_tokens=500)

    # 대화 시작
    print(f"설정: {config.gpt_role} 역할, 난이도: {config.difficulty.value}")
    print("\n대화를 시작합니다...\n")

    # 첫 번째 메시지
    user_message = "안녕하세요, 메뉴판 좀 볼 수 있을까요?"
    print(f"사용자: {user_message}")

    response = service.send(user_message)
    print(f"\n{config.gpt_role}: {response}")

    # 추천 표현 출력
    print("\n--- 추천 표현 ---")
    print("이어서 쓸 수 있는 표현들:")
    for phrase in response.suggested_phrases:
        print(f"  • {phrase}")

    # 사용량 정보 출력
    if response.usage:
        print(f"\n--- 토큰 사용량 ---")
        print(f"{response.usage}")

    # 두 번째 메시지
    user_message2 = "김치찌개 하나 주문할게요."
    print(f"\n사용자: {user_message2}")

    response2 = service.send(user_message2)
    print(f"\n{config.gpt_role}: {response2}")

    # 대화 기록 확인
    print("\n--- 대화 기록 ---")
    messages = chat_store.get_messages()
    for msg in messages:
        role_name = "사용자" if msg.role == "user" else config.gpt_role
        print(f"{role_name}: {msg.content[:50]}...")
        if msg.usage:
            print(f"  → 토큰: {msg.usage.total_tokens}")


def test_different_difficulties():
    """다양한 난이도 테스트"""
    print("\n" + "=" * 50)
    print("난이도별 응답 비교")
    print("=" * 50)

    user_message = "예약하고 싶어요"

    for difficulty in [Difficulty.BEGINNER, Difficulty.INTERMEDIATE, Difficulty.ADVANCED]:
        config = RolePlayChatConfig(
            language="한국어",
            user_role="손님",
            gpt_role="웨이터",
            difficulty=difficulty,
            role_template=STARBUCKS_PROMPT,
        )

        service = ChatService(config=config, temperature=0.8, max_tokens=300)

        print(f"\n[{difficulty.value}]")
        response = service.send(user_message)
        print(f"응답: {response}")
        print(f"추천 표현 수: {len(response.suggested_phrases)}")


if __name__ == "__main__":
    # OpenAI API 키 확인
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY 환경 변수를 설정해주세요.")
        print("export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)

    try:
        # 테스트 실행
        test_non_streaming()
        test_different_difficulties()

    except FileNotFoundError as e:
        print(f"\nError: 프롬프트 파일을 찾을 수 없습니다: {e}")
        print("roleplay/templates/prompts/ 디렉토리에 starbucks.txt와 starbucks.txt 파일이 있는지 확인해주세요.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
