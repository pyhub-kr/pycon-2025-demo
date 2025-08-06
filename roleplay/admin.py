from django.contrib import admin
from .models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """채팅 세션 Admin"""

    list_display = [
        "id",
        "title_display",
        "user",
        "model",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "model", "created_at"]
    search_fields = ["title", "instruction", "user__username"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("기본 정보", {"fields": ("user", "title", "is_active")}),
        ("시스템 프롬프트", {"fields": ("instruction",)}),
        ("AI 모델 설정", {"fields": ("model", "temperature", "max_tokens")}),
        (
            "타임스탬프",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def title_display(self, obj):
        """제목 표시 (없으면 Session #ID)"""
        return obj.title or f"Session #{obj.id}"

    title_display.short_description = "Title"


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """채팅 메시지 Admin"""

    list_display = [
        "id",
        "session",
        "role",
        "content_preview",
        "created_at",
    ]
    list_filter = ["role", "created_at"]
    search_fields = ["content", "session__title"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["session"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("세션 정보", {"fields": ("session",)}),
        ("메시지 정보", {"fields": ("role", "content")}),
        (
            "생성 시간",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )

    def content_preview(self, obj):
        """내용 미리보기"""
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content

    content_preview.short_description = "Content Preview"


# Admin 사이트 커스터마이징
admin.site.site_header = "채팅 히스토리 관리"
admin.site.site_title = "Chat Admin"
admin.site.index_title = "채팅 세션 및 메시지 관리"
