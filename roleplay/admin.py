from django.contrib import admin
from .models import GeneralChatSession, RolePlayChatSession, ChatMessage


# 새로운 모델들의 Admin 클래스


@admin.register(GeneralChatSession)
class GeneralChatSessionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "purpose",
        "user",
        "total_tokens",
        "is_active",
        "created_at",
    ]
    list_filter = ["purpose", "is_active", "created_at"]
    search_fields = ["title", "context", "user__username"]
    readonly_fields = ["created_at", "updated_at", "input_tokens", "output_tokens", "total_tokens"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("기본 정보", {"fields": ("user", "title", "purpose", "is_active")}),
        ("컨텍스트", {"fields": ("context", "system_prompt")}),
        ("모델 설정", {"fields": ("model", "temperature", "max_tokens")}),
        (
            "토큰 사용량",
            {
                "fields": ("input_tokens", "output_tokens", "total_tokens"),
                "classes": ("collapse",),
            },
        ),
        (
            "타임스탬프",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(RolePlayChatSession)
class RolePlayChatSessionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "prompt_name",
        "language",
        "difficulty",
        "user",
        "total_tokens",
        "is_active",
        "created_at",
    ]
    list_filter = ["language", "difficulty", "is_active", "created_at"]
    search_fields = ["prompt_name", "title", "user__username"]
    readonly_fields = ["created_at", "updated_at", "input_tokens", "output_tokens", "total_tokens"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("기본 정보", {"fields": ("user", "title", "is_active")}),
        ("역할극 설정", {"fields": ("prompt_name", "language", "user_role", "gpt_role", "difficulty")}),
        ("프롬프트", {"fields": ("system_prompt",)}),
        ("모델 설정", {"fields": ("model", "temperature", "max_tokens")}),
        (
            "토큰 사용량",
            {
                "fields": ("input_tokens", "output_tokens", "total_tokens"),
                "classes": ("collapse",),
            },
        ),
        (
            "타임스탬프",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ["id", "session_info", "role", "content_preview", "total_tokens_display", "created_at"]
    list_filter = ["role", "created_at", "content_type"]
    search_fields = ["content"]
    readonly_fields = ["created_at", "input_tokens", "output_tokens", "content_type", "object_id"]
    date_hierarchy = "created_at"

    # Generic FK는 raw_id_fields를 직접 사용할 수 없으므로 제거
    # raw_id_fields = []

    fieldsets = (
        ("세션 정보", {"fields": ("content_type", "object_id")}),
        ("메시지 정보", {"fields": ("role", "content", "created_at")}),
        (
            "토큰 사용량",
            {
                "fields": ("input_tokens", "output_tokens"),
                "classes": ("collapse",),
                "description": "Assistant 메시지에만 해당",
            },
        ),
    )

    def session_info(self, obj):
        """세션 정보를 표시"""
        session = obj.session
        if session:
            if hasattr(session, "prompt_name"):
                return f"{session.prompt_name} (ID: {session.id})"
            elif hasattr(session, "title"):
                return f"{session.title or 'Untitled'} (ID: {session.id})"
            else:
                return f"Session {session.id}"
        return "-"

    session_info.short_description = "Session"

    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content

    content_preview.short_description = "Content Preview"

    def total_tokens_display(self, obj):
        if obj.input_tokens and obj.output_tokens:
            return obj.input_tokens + obj.output_tokens
        return "-"

    total_tokens_display.short_description = "Total Tokens"
