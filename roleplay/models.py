from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# Abstract Base Model
class AbstractChatSession(models.Model):
    """모든 채팅 세션의 기본 추상 모델"""

    # 공통 필드
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, blank=True, help_text="세션 제목")

    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # 토큰 사용량 추적
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)

    # 설정 저장
    system_prompt = models.TextField(blank=True, help_text="실제 사용된 시스템 프롬프트")

    # 모델 설정 필드들
    model = models.CharField(max_length=50, default="gpt-4o", help_text="사용할 AI 모델")
    temperature = models.FloatField(default=1.0, help_text="응답의 창의성 정도 (0.0~2.0)")
    max_tokens = models.IntegerField(default=1000, help_text="최대 응답 토큰 수")

    class Meta:
        abstract = True
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title or f"Session {self.id}"

    @property
    def total_tokens(self):
        """총 토큰 사용량"""
        return self.input_tokens + self.output_tokens


# Concrete Models
class GeneralChatSession(AbstractChatSession):
    """일반 채팅 세션 - 단순 대화용"""

    class PurposeChoices(models.TextChoices):
        GENERAL = "general", "일반 대화"
        QA = "qa", "질문/답변"
        CUSTOMER_SUPPORT = "customer_support", "고객 지원"
        EDUCATION = "education", "교육"
        OTHER = "other", "기타"

    # 일반 채팅 전용 필드
    purpose = models.CharField(
        max_length=50, choices=PurposeChoices.choices, default=PurposeChoices.GENERAL, help_text="채팅 목적"
    )
    context = models.TextField(blank=True, help_text="추가 컨텍스트 정보")

    class Meta:
        # db_table = "chat_general_session"
        verbose_name = "일반 채팅 세션"
        verbose_name_plural = "일반 채팅 세션들"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["purpose", "created_at"]),
        ]


class RolePlayChatSession(AbstractChatSession):
    """역할극 전용 세션"""

    class DifficultyChoices(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    # 역할극 전용 필드
    prompt_name = models.CharField(max_length=100, help_text="프롬프트 이름")
    language = models.CharField(max_length=50, help_text="학습 언어")
    user_role = models.CharField(max_length=200, help_text="사용자 역할")
    gpt_role = models.CharField(max_length=200, help_text="AI 역할")
    difficulty = models.CharField(
        max_length=20, choices=DifficultyChoices.choices, default=DifficultyChoices.BEGINNER, help_text="난이도"
    )

    class Meta:
        # db_table = "chat_roleplay_session"
        verbose_name = "역할극 채팅 세션"
        verbose_name_plural = "역할극 채팅 세션들"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["language", "difficulty"]),
        ]

    def save(self, *args, **kwargs):
        # title이 비어있으면 자동 생성
        if not self.title:
            self.title = f"{self.prompt_name} - {self.language}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prompt_name} - {self.language} (ID: {self.id})"


class ChatMessage(models.Model):
    """모든 채팅 타입에서 공용으로 사용하는 메시지 모델"""

    class RoleChoices(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"
        SYSTEM = "system", "System"

    # Generic Foreign Key를 사용하여 다양한 세션 타입 지원
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"model__in": ("generalchatsession", "roleplaychatsession")},
        null=True,  # 기존 데이터 마이그레이션을 위해 임시로 null 허용
        blank=True,
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)  # 기존 데이터 마이그레이션을 위해 임시로 null 허용
    session = GenericForeignKey("content_type", "object_id")

    # 메시지 기본 정보
    role = models.CharField(max_length=20, choices=RoleChoices.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # OpenAI API 사용량 추적 (assistant 메시지에만 해당)
    input_tokens = models.PositiveIntegerField(null=True, blank=True)
    output_tokens = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        # db_table = "roleplay_chat_message"
        verbose_name = "채팅 메시지"
        verbose_name_plural = "채팅 메시지들"
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["role", "created_at"]),
        ]

    def __str__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.role}: {content_preview}"

    def get_session(self):
        """세션 객체 반환"""
        return self.session
