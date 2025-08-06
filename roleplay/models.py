from django.db import models
from django.contrib.auth.models import User


class ChatSession(models.Model):
    """단순한 채팅 세션 모델"""

    # 기본 정보
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, blank=True, help_text="세션 제목")
    instruction = models.TextField(help_text="시스템 프롬프트 (SimpleChatConfig의 instruction)")

    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # AI 설정 (선택적)
    model = models.CharField(max_length=50, default="gpt-4o", help_text="사용할 AI 모델")
    temperature = models.FloatField(default=1.0, help_text="응답의 창의성 정도 (0.0~2.0)")
    max_tokens = models.IntegerField(default=1000, help_text="최대 응답 토큰 수")

    class Meta:
        verbose_name = "채팅 세션"
        verbose_name_plural = "채팅 세션들"
        ordering = ["-pk"]

    def __str__(self):
        return self.title or f"Session #{self.id}"


class ChatMessage(models.Model):
    """채팅 메시지 모델"""

    class RoleChoices(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"
        SYSTEM = "system", "System"

    # 세션과의 관계
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")

    # 메시지 정보
    role = models.CharField(max_length=20, choices=RoleChoices.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "채팅 메시지"
        verbose_name_plural = "채팅 메시지들"
        ordering = ["pk"]

    def __str__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.role}: {content_preview}"
