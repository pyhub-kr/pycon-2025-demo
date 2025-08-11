from django.contrib import admin
from .models import Prompt


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    """프롬프트 Admin 설정"""

    list_display = ["title", "category", "usage_count", "is_favorite", "created_at"]
    list_filter = ["category", "is_favorite", "created_at"]
    search_fields = ["title", "content", "tags"]
    readonly_fields = ["usage_count", "created_at", "updated_at"]

    fieldsets = (
        ("기본 정보", {"fields": ("title", "category", "is_favorite")}),
        ("내용", {"fields": ("content", "tags"), "classes": ("wide",)}),
        ("통계", {"fields": ("usage_count", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_readonly_fields(self, request, obj=None):
        """수정 시 title을 읽기 전용으로 (unique 제약)"""
        if obj:  # 수정 모드
            return self.readonly_fields + ["title"]
        return self.readonly_fields
