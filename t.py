from roleplay.models import ChatSession, ChatMessage

# 새로운 세션 생성
session = ChatSession.objects.create(
    user=user,
    instruction="You're a helpful assistant.",
    model="gpt-4o",
    temperature=1.0,
    max_tokens=1000,
)

# 대화 메시지 저장
ChatMessage.objects.create(session=session, role="user", content="hello")
session.message_set.create(role="assistant", content="Can I help you?")

# 세션의 모든 메시지 조회
message_qs = ChatMessage.objects.filter(session=session)
message_qs = session.message_set.all()

# 세션의 모든 메시지를 삭제
message_qs.delete()
