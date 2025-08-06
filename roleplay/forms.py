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
        
        # 레이아웃 정의
        self.helper.layout = Layout(
            Field('title', css_class='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'),
            Field('instruction', rows=4, css_class='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'),
            Row(
                Column(
                    Field('model', css_class='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'),
                    css_class='form-group col-md-4'
                ),
                Column(
                    Field('temperature', css_class='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'),
                    css_class='form-group col-md-4'
                ),
                Column(
                    Field('max_tokens', css_class='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'),
                    css_class='form-group col-md-4'
                ),
                css_class='grid grid-cols-3 gap-4'
            ),
            FormActions(
                Submit('submit', '세션 생성', css_class='bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors'),
                HTML('<a href="{% url "roleplay:chatsession_list" %}" class="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300 transition-colors ml-3">취소</a>')
            )
        )
