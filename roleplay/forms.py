# roleplay/forms.py

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, Submit, HTML
from .models import ChatSession


class ChatSessionForm(forms.ModelForm):
    class Meta:
        model = ChatSession
        fields = [
            "title",
            "instruction",
            "model",
            "temperature",
            "max_tokens",
        ]

    # django-crispy-forms를 통해 폼 렌더링 커스터마이징
    # FormHelper 설정
    helper = FormHelper()
    helper.form_method = "post"
    helper.form_class = "space-y-4"
    helper.attrs = {"novalidate": ""}

    # 공통 input 스타일
    input_class = (
        "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    )

    # 레이아웃 정의
    helper.layout = Layout(
        Field("title", css_class=input_class),
        Field("instruction", rows=4, css_class=input_class),
        Div(
            Field("model", css_class=input_class, wrapper_class="flex-1"),
            Field("temperature", css_class=input_class, wrapper_class="flex-1"),
            Field("max_tokens", css_class=input_class, wrapper_class="flex-1"),
            css_class="flex gap-4",
        ),
        Div(
            Submit(
                "submit",
                "세션 생성",
                css_class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors",
            ),
            HTML(
                '<a href="{% url "roleplay:chatsession_list" %}" class="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">취소</a>'
            ),
            css_class="flex gap-3 mt-6",
        ),
    )
