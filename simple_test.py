#!/usr/bin/env python

"""가장 간단한 RolePlay 테스트"""

# 장고 프로젝트 외부에서 장고 프로젝트 내부 리소스에 접근하기 위한 초기화
import os
from typing import Optional

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
import django

django.setup()

# 장고 프로젝트 내부 리소스에 접근
from roleplay.core import SimpleChatConfig, ChatService
from roleplay.django_stores import DjangoChatHistoryStore

config = SimpleChatConfig(instruction="You're a helpful assistant.")

session_id: Optional[int] = None  # 새로운 대화방 세션 생성
store = DjangoChatHistoryStore(session_id=session_id, config=config)
service = ChatService(config=config, chat_history_store=store)

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
