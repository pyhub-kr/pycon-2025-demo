#!/usr/bin/env python

"""English Roleplay Practice - Starbucks Ordering Scenario"""

import os
from roleplay.core import ChatService, RolePlayChatConfig, Difficulty, InMemoryStore
from roleplay.prompts import STARBUCKS_PROMPT

# API 키 확인
if not os.environ.get("OPENAI_API_KEY"):
    print("Please run: export OPENAI_API_KEY='your-api-key'")
    exit(1)

# 설정 - 구체적인 상황 설정
config = RolePlayChatConfig(
    language="English",
    user_role="a tourist visiting New York who wants to order coffee and needs help with customization options",
    gpt_role="a friendly Starbucks barista named Sarah who works at Times Square location",
    difficulty=Difficulty.INTERMEDIATE,
    role_template=STARBUCKS_PROMPT,
)

# 서비스 생성
service = ChatService(
    config=config,
    chat_history_store=InMemoryStore(),
    verbose=False,  # Set to True to see prompts
)

# 대화 시작
print("=== Starbucks Coffee Ordering Roleplay ===")
print(f"📍 Location: Starbucks at Times Square, New York")
print(f"👤 You are: {config.user_role}")
print(f"☕ Barista: {config.gpt_role}")
print(f"📚 Difficulty: {config.difficulty.value}")
print("\n" + "=" * 70 + "\n")

# 첫 번째 대화 - 인사와 주문 시작
user_msg1 = "Hi, I'd like to order a coffee but I'm not sure what to get. What do you recommend?"
print(f"You: {user_msg1}")

response = service.send(user_msg1)
print(f"\nBarista Sarah: {response.main_response}")
print("\n💡 Suggested Phrases:")
for phrase in response.suggested_phrases[:3]:
    print(f"  • {phrase}")
if response.usage:
    print(f"📊 Token Usage: {response.usage}")

print("\n" + "=" * 70 + "\n")

# 두 번째 대화 - 사이즈와 커스터마이징
user_msg2 = "What sizes do you have? And can I make it less sweet?"
print(f"You: {user_msg2}")

response2 = service.send(user_msg2)
print(f"\nBarista Sarah: {response2.main_response}")
print("\n💡 Suggested Phrases:")
for phrase in response2.suggested_phrases:
    print(f"  • {phrase}")

if response2.usage:
    print(f"\n📊 Token Usage: Input {response2.usage.input_tokens}, Output {response2.usage.output_tokens}")

# 세 번째 대화 - 실제 주문 완성
print("\n" + "=" * 70 + "\n")
user_msg3 = "I'll have a grande iced latte with oat milk and one pump of vanilla, please."
print(f"You: {user_msg3}")

response3 = service.send(user_msg3)
print(f"\nBarista Sarah: {response3.main_response}")
print("\n💡 Suggested Phrases:")
for phrase in response3.suggested_phrases[:3]:
    print(f"  • {phrase}")

print("\n🎯 Practice Summary:")
print("You've practiced ordering coffee at Starbucks including:")
print("  • Asking for recommendations")
print("  • Inquiring about sizes and customizations")
print("  • Making a specific order with modifications")
