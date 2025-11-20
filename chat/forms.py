from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
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

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'location']
        widgets = {
            'bio': forms.Textarea(attrs={'placeholder': 'Tell us about yourself...', 'rows': 4}),
            'location': forms.TextInput(attrs={'placeholder': 'Your location'}),
        }
