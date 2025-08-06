from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView

from .core import (
    ChatResponse,
    SimpleChatConfig,
    RolePlayChatConfig,
    Difficulty,
    ChatService,
)
from .forms import ChatSessionForm

from .models import ChatSession


class ChatSessionListView(LoginRequiredMixin, ListView):
    model = ChatSession

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


class ChatSessionCreateView(LoginRequiredMixin, CreateView):
    model = ChatSession
    form_class = ChatSessionForm

    def form_valid(self, form):
        chatsession = form.save(commit=False)
        chatsession.user = self.request.user
        return super().form_valid(form)


class ChatSessionUpdateView(LoginRequiredMixin, UpdateView):
    model = ChatSession
    form_class = ChatSessionForm

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


@login_required
def chat(request) -> HttpResponse:
    """통합된 채팅 뷰 - HTML 렌더링과 API 응답 모두 처리"""

    # 데이터베이스에서 조회하기 (추후 구현)
    config = SimpleChatConfig(instruction="You're a helpful assistant.")
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
