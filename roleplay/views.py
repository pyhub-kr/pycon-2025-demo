from typing import Generator

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .core import ChatResponse, SimpleChatConfig, ChatService, Message
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
def chat(request, pk) -> HttpResponse | StreamingHttpResponse:
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

    else:
        def make_stream() -> Generator[str, None, None]:
            try:
                # TODO: Django Form 등을 활용한 유효성 검사
                message = request.POST.get("message", "").strip()
                if not message:
                    yield render_to_string(
                        template_name="roleplay/_chat_response.html",
                        context={"error_message": "Message is required."},
                        request=request,
                    )

                human_message = Message(role="user", content=message)
                ai_message = Message(role="assistant", content="Loading ...")

                yield render_to_string(
                    template_name="roleplay/_chat_response.html",
                    context={"human_message": human_message, "ai_message": ai_message},
                    request=request,
                )

                config = SimpleChatConfig(instruction=session.instruction)
                chat_service = ChatService(
                    config=config,
                    model=session.model,
                    temperature=session.temperature,
                    max_tokens=session.max_tokens,
                    chat_history_store=store,
                )
                chat_response: ChatResponse = chat_service.send(message)
                ai_message.content = str(chat_response)
                yield render_to_string(
                    template_name="roleplay/_chat_response.html",
                    context={"chat_response": chat_response, "ai_message": ai_message},
                    request=request,
                )
            except Exception as e:
                yield render_to_string(
                    template_name="roleplay/_chat_response.html",
                    context={"error_message": str(e)},
                    request=request,
                )

        response = StreamingHttpResponse(make_stream(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["X-Accel-Buffering"] = "no"  # nginx 버퍼링 비활성화
        return response
