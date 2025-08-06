#!/usr/bin/env python
"""Verbose 모드 테스트 - 프롬프트 내역 출력 비교"""
import os
from roleplay.core import ChatService, RolePlayChatConfig, Difficulty, InMemoryStore
from roleplay.prompts import CAFE_STAFF_PROMPT

# API 키 확인
if not os.environ.get("OPENAI_API_KEY"):
    print("export OPENAI_API_KEY='your-api-key' 를 먼저 실행하세요.")
    exit(1)

print("=" * 70)
print("=== Verbose 모드 비교 테스트 ===")
print("=" * 70)

# 1. Verbose OFF (기본값)
print("\n[1] Verbose=False (기본 모드)")
print("-" * 50)

config_normal = RolePlayChatConfig(
    language="한국어",
    user_role="손님",
    gpt_role="웨이터",
    difficulty=Difficulty.BEGINNER,
    role_template=CAFE_STAFF_PROMPT,
)

service_normal = ChatService(
    config=config_normal,
    chat_history_store=InMemoryStore(),
    verbose=False,  # 기본값
)

response = service_normal.send("메뉴판 좀 주세요")
print(f"웨이터: {response.main_response}")

# 2. Verbose ON
print("\n\n[2] Verbose=True (디버그 모드)")
print("-" * 50)

config_verbose = RolePlayChatConfig(
    language="한국어",
    user_role="손님",
    gpt_role="웨이터",
    difficulty=Difficulty.BEGINNER,
    role_template=CAFE_STAFF_PROMPT,
)

service_verbose = ChatService(
    config=config_verbose,
    chat_history_store=InMemoryStore(),
    verbose=True,  # 프롬프트 출력
)

response = service_verbose.send("메뉴판 좀 주세요")
print(f"\n웨이터: {response.main_response}")

# 3. 대화 이어가기 (히스토리 포함)
print("\n\n[3] 대화 이어가기 - Verbose 모드로 히스토리 확인")
print("-" * 50)

response = service_verbose.send("김치찌개 하나 주문할게요")
print(f"\n웨이터: {response.main_response}")

print("\n\n💡 Verbose 모드 활용 팁:")
print("- 프롬프트 최적화를 위한 디버깅")
print("- 토큰 사용량 모니터링")
print("- 대화 컨텍스트 추적")
print("- API 설정 확인")
