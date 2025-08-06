# roleplay/admin.py

from django.contrib import admin
from .models import ChatSession

# Admin 사이트 커스터마이징
admin.site.site_header = "파이콘 2025"
admin.site.site_title = "파이콘 2025"
# admin.site.index_title = "채팅 세션 조회"


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """채팅 세션 Admin (읽기 전용)"""

    list_display = ["id", "title_display", "user", "model", "created_at"]
    list_filter = ["model", "created_at"]
    search_fields = ["title", "instruction", "user__username"]
    date_hierarchy = "created_at"

    # 모든 필드를 읽기 전용으로 설정
    readonly_fields = [
        "user",
        "title",
        "instruction",
        "model",
        "temperature",
        "max_tokens",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        ("기본 정보", {"fields": ("user", "title")}),
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

    def has_add_permission(self, request):
        """추가 권한 제거"""
        return False

    def has_change_permission(self, request, obj=None):
        """수정 권한 제거 (조회만 가능)"""
        return True  # True를 반환해야 조회가 가능

    def has_delete_permission(self, request, obj=None):
        """삭제 권한 제거"""
        return False
