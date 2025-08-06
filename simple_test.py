#!/usr/bin/env python

"""가장 간단한 RolePlay 테스트"""

from roleplay.core import RolePlayChatConfig, InMemoryStore, ChatService, Difficulty

# config = SimpleChatConfig(instruction="You're a helpful assistant.")

role_template = """You are a friendly barista at Starbucks.
You help customers order coffee and provide recommendations.

Menu:
- Coffee: Americano, Latte, Cappuccino
- Sizes: Tall, Grande, Venti
- Customizations: Different milk options, syrups

Be friendly and helpful in your responses."""

config = RolePlayChatConfig(
    language="English",
    user_role="커피 주문하는 손님이며, 이름은 이진석",
    gpt_role="스타벅스 직원이며, 이름은 John.",
    difficulty=Difficulty.BEGINNER,
    role_template=role_template,
)

service = ChatService(config=config, chat_history_store=InMemoryStore())

# 생략

human_message = "Can I get a coffee?"
print("Human :", human_message)
response = service.send(human_message)
print("AI :", response)

human_message = "One Ice Americano, please."
print("Human :", human_message)
response = service.send(human_message)
print("AI :", response)

print("\n=== 추천 표현 ===")
print("이어서 쓸 수 있는 표현들:")
for phrase in response.suggested_phrases:
    print(f"  • {phrase}")

#
# while True:
#     if human_message := input("Human: ").strip():
#         response = service.send(human_message)
#         print(f"AI: {response.main_response}")
#
#         print()
#         print("----")
#         print("추천 표현:")
#         for phrase in response.suggested_phrases:
#             print("\t" + phrase)
#         print("----")
#         print()
#
#         print("\tresponse.suggested_phrases :", repr(response.suggested_phrases))
#         print("\tresponse.usage :", repr(response.usage))
#     else:
#         break
