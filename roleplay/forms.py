from django import forms
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
