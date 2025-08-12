from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="유효한 이메일 주소를 입력해주세요.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("username", css_class="mb-4"),
            Field("email", css_class="mb-4"),
            Field("password1", css_class="mb-4"),
            Field("password2", css_class="mb-4"),
            Submit(
                "submit",
                "회원가입",
                css_class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded",
            ),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ProfileEditForm(UserChangeForm):
    password = None  # 비밀번호 필드 숨기기

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column(Field("username", css_class="mb-4"), css_class="col-md-6"),
                Column(Field("email", css_class="mb-4"), css_class="col-md-6"),
            ),
            Row(
                Column(Field("first_name", css_class="mb-4"), css_class="col-md-6"),
                Column(Field("last_name", css_class="mb-4"), css_class="col-md-6"),
            ),
            Submit(
                "submit",
                "프로필 수정",
                css_class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded",
            ),
        )
