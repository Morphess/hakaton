from django import forms
from .models import ChatMessage, PDFDocument

class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = PDFDocument
        fields = ['title', 'file']

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введіть повідомлення'}),
        }