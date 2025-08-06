from roleplay.core import SimpleChatConfig, InMemoryStore, ChatService

config = SimpleChatConfig(instruction="You're a helpful assistant.")

store = InMemoryStore()
service = ChatService(config=config, chat_history_store=store)

human_message = "Hello. My name is Chinseok."
print("Human :", human_message)
response = service.send(human_message)
print("AI :", response)

human_message = "What's my name?"
print("Human :", human_message)
response = service.send(human_message)
print("AI :", response)

print("\n=== 이어서 쓸 수 있는 표현들 ===")
for phrase in response.suggested_phrases:
    print(f"  • {phrase}")
