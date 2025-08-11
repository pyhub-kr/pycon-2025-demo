"""
Mixin 재사용성 테스트를 위한 예제 Form
"""

from django import forms
from .forms_base import HTMXValidationMixin, BaseHTMXForm


class ContactForm(BaseHTMXForm):
    """연락처 폼 - BaseHTMXForm 상속 예제"""

    name = forms.CharField(label="이름", max_length=100, min_length=2, required=True)

    email = forms.EmailField(label="이메일", required=True)

    message = forms.CharField(label="메시지", widget=forms.Textarea, min_length=10, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # HTMX 속성 자동 추가
        self.setup_htmx_attributes()

    def clean_name(self):
        name = self.cleaned_data.get("name", "")
        if len(name) < 2:
            raise forms.ValidationError("이름은 2자 이상이어야 합니다.")
        return name


class SimpleForm(HTMXValidationMixin, forms.Form):
    """간단한 폼 - Mixin 직접 사용 예제"""

    username = forms.CharField(label="사용자명", max_length=50, required=True)

    age = forms.IntegerField(label="나이", min_value=1, max_value=150, required=True)

    agree = forms.BooleanField(label="동의", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 특정 필드만 HTMX 적용
        self.setup_htmx_attributes(["username", "age"])
