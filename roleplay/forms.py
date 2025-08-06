from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column, Submit, HTML
from crispy_forms.bootstrap import FormActions
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
        
        # 폼 필드 기본 클래스 설정
        self.helper.field_class = 'form-control'
        
        # 레이아웃 정의
        self.helper.layout = Layout(
            Field('title'),
            Field('instruction', rows=4),
            Row(
                Column('model', css_class='col-md-4'),
                Column('temperature', css_class='col-md-4'),
                Column('max_tokens', css_class='col-md-4'),
                css_class='row'
            ),
            FormActions(
                Submit('submit', '세션 생성', css_class='btn btn-primary'),
                HTML('<a href="{% url "roleplay:chatsession_list" %}" class="btn btn-secondary ml-2">취소</a>')
            )
        )
