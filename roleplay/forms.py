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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # FormHelper 설정
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-4'
        
        # 레이아웃 정의
        self.helper.layout = Layout(
            Field('title', css_class='form-control'),
            Field('instruction', rows=4, css_class='form-control'),
            Div(
                Div(Field('model', css_class='form-control'), css_class='flex-1'),
                Div(Field('temperature', css_class='form-control'), css_class='flex-1'),
                Div(Field('max_tokens', css_class='form-control'), css_class='flex-1'),
                css_class='flex gap-4'
            ),
            Div(
                Submit('submit', '세션 생성', css_class='btn-primary'),
                HTML('<a href="{% url "roleplay:chatsession_list" %}" class="btn-secondary">취소</a>'),
                css_class='flex gap-3 mt-6'
            )
        )
