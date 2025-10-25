from django import forms
from .models import Thread, Reply, UserProfile

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title', 'content', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Thread Title'}),
            'content': forms.Textarea(attrs={'placeholder': 'Thread Content', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'category-select'}),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Reply...', 'rows': 2}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'location']
        widgets = {
            'bio': forms.Textarea(attrs={'placeholder': 'Tell us about yourself...', 'rows': 4}),
            'location': forms.TextInput(attrs={'placeholder': 'Your location'}),
        }
