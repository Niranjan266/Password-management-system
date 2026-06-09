from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import PasswordEntry, CATEGORY_CHOICES

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    pass

class PasswordEntryForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(render_value=True))
    
    class Meta:
        model = PasswordEntry
        fields = ['platform', 'username', 'password', 'url', 'category', 'notes', 'is_favorite']
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.password = self.cleaned_data['password']
        if commit:
            instance.save()
        return instance
