from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .core import ChatResponse, SimpleChatConfig, ChatService
from .django_stores import DjangoChatHistoryStore
from .forms import ChatSessionForm

from .models import ChatSession


class ChatSessionListView(LoginRequiredMixin, ListView):
    model = ChatSession
    # paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


class ChatSessionCreateView(LoginRequiredMixin, CreateView):
    model = ChatSession
    form_class = ChatSessionForm
    success_url = reverse_lazy("roleplay:chatsession_list")

    def form_valid(self, form):
        chatsession = form.save(commit=False)
        chatsession.user = self.request.user
        return super().form_valid(form)


class ChatSessionUpdateView(LoginRequiredMixin, UpdateView):
    model = ChatSession
    form_class = ChatSessionForm
    success_url = reverse_lazy("roleplay:chatsession_list")

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


@login_required
def chat(request, pk) -> HttpResponse:
    """통합된 채팅 뷰 - HTML 렌더링과 API 응답 모두 처리"""
    
    session = get_object_or_404(ChatSession, pk=pk, user=request.user)
    store = DjangoChatHistoryStore(session=session)

    if request.method == "GET":
        message_list = store.get_messages()
        context_data = {
            "session": session,
            "message_list": message_list,
        }
        return render(request, "roleplay/chat.html", context_data)

    elif request.method == "POST":
        # TODO: Django Form 등을 활용한 유효성 검사
        message = request.POST.get("message", "").strip()
        if not message:
            return JsonResponse({"error": "Message is required"}, status=400)

        config = SimpleChatConfig(instruction=session.instruction)
        chat_service = ChatService(
            config=config,
            model=session.model,
            temperature=session.temperature,
            max_tokens=session.max_tokens,
            chat_history_store=store,
        )
        response: ChatResponse = chat_service.send(message)
        return JsonResponse(response.to_dict())

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
