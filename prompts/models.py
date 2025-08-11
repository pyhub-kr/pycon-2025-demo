from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from .validators import (
    get_title_validators,
    get_content_validators,
    get_tags_validators,
)


class Prompt(models.Model):
    CATEGORY_CHOICES = [
        ("writing", "글쓰기"),
        ("coding", "코딩"),
        ("analysis", "분석"),
        ("creative", "창작"),
        ("business", "비즈니스"),
        ("education", "교육"),
        ("other", "기타"),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name="제목",
        unique=True,  # 중복 방지
        validators=get_title_validators(),
        help_text="5-200자, 특수문자 제한",
    )
    content = models.TextField(
        verbose_name="프롬프트 내용",
        validators=get_content_validators(),
        help_text="최소 50자, [변수명] 형식으로 변수 사용 가능",
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="other", verbose_name="카테고리")
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name="태그",
        validators=get_tags_validators(),
        help_text="최대 10개, 각 태그 2-20자",
    )
    usage_count = models.IntegerField(default=0, verbose_name="사용 횟수")
    is_favorite = models.BooleanField(default=False, verbose_name="즐겨찾기")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        ordering = ["-is_favorite", "-usage_count", "-created_at"]
        verbose_name = "프롬프트"
        verbose_name_plural = "프롬프트"

    def __str__(self):
        return self.title

    def increment_usage(self):
        """사용 횟수 증가"""
        self.usage_count += 1
        self.save(update_fields=["usage_count"])

    def clean(self):
        """모델 레벨 추가 검증"""
        super().clean()

        # tags가 문자열로 들어온 경우 리스트로 변환
        if isinstance(self.tags, str):
            self.tags = [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    @classmethod
    def search(cls, query):
        """프롬프트 검색"""
        if not query:
            return cls.objects.all()

        return cls.objects.filter(Q(title__icontains=query) | Q(content__icontains=query) | Q(tags__icontains=query))
