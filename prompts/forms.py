import json
from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
from .models import Prompt
from .forms_base import HTMXValidationMixin


class PromptForm(HTMXValidationMixin, forms.ModelForm):
    """프롬프트 생성/수정 폼"""

    # URL reverse를 위한 URL 이름 설정
    validation_url_name = "prompts:validate_field"

    tags = forms.CharField(
        label="태그",
        required=False,
        help_text="쉼표로 구분하여 입력 (예: python, 코드리뷰, 최적화)",
        widget=forms.TextInput(
            attrs={
                "placeholder": "태그1, 태그2, 태그3",
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
            }
        ),
    )

    class Meta:
        model = Prompt
        fields = ["title", "content", "category", "tags", "is_favorite"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "프롬프트 제목을 입력하세요 (5-200자)",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "rows": 8,
                    "placeholder": "프롬프트 내용을 입력하세요 (최소 50자)\n[변수명] 형식으로 변수를 표시할 수 있습니다.",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "is_favorite": forms.CheckboxInput(
                attrs={
                    "class": "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 초기값 설정 (수정 시)
        if self.instance and self.instance.pk:
            if self.instance.tags:
                self.fields["tags"].initial = ", ".join(self.instance.tags)

        # FormHelper 설정
        self.helper = FormHelper()
        self.helper.form_id = "prompt-form"
        self.helper.form_method = "post"
        self.helper.form_class = "space-y-6"

        # HTMX 속성 자동 추가 (Mixin 메서드 사용)
        self.setup_htmx_attributes(["title", "content", "category", "tags"])

    def clean_tags(self):
        """태그 문자열을 리스트로 변환 - 검증은 모델 validators가 처리"""
        tags_str = self.cleaned_data.get("tags", "")

        if isinstance(tags_str, list):
            return tags_str

        # 쉼표로 분리하고 정리
        tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
        return tags
