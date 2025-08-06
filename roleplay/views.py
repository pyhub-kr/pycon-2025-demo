from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .core import (
    ChatResponse,
    SimpleChatConfig,
    RolePlayChatConfig,
    Difficulty,
    ChatService,
)
from .prompts import STARBUCKS_PROMPT


@login_required
def chat(request) -> HttpResponse:
    """통합된 채팅 뷰 - HTML 렌더링과 API 응답 모두 처리"""

    # 데이터베이스에서 조회하기 (추후 구현)
    config = SimpleChatConfig(instruction="You're a helpful assistant.")
    # config = RolePlayChatConfig(
    #     language="ko",
    #     user_role="고객",
    #     gpt_role="직원",
    #     difficulty=Difficulty.BEGINNER,
    #     role_template=STARBUCKS_PROMPT,
    # )
    chat_service = ChatService(
        config=config,
        model="gpt-4o-mini",
    )

    if request.method == "GET":
        return render(request, "roleplay/chat.html")

    elif request.method == "POST":
        # Django Form 등을 활용한 유효성 검사
        message = request.POST.get("message", "").strip()
        if not message:
            return JsonResponse({"error": "Message is required"}, status=400)

        response: ChatResponse = chat_service.send(message)
        return JsonResponse(response.to_dict())

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
