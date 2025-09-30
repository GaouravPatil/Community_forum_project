from django import forms
from .models import Thread, Reply

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Thread Title'}),
            'content': forms.Textarea(attrs={'placeholder': 'Thread Content', 'rows': 3}),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Reply...', 'rows': 2}),
        }
