from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import DataPlatform, PasswordEntry, CATEGORY_CHOICES

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
        fields = ['platform', 'logo_url', 'logo', 'username', 'password', 'url', 'category', 'notes', 'is_favorite']

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo and logo.size > 2 * 1024 * 1024:
            raise forms.ValidationError('Logo must be smaller than 2 MB.')
        content_type = getattr(logo, 'content_type', '')
        if content_type and not content_type.startswith('image/'):
            raise forms.ValidationError('Please upload an image file.')
        return logo
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.password = self.cleaned_data['password']
        if commit:
            instance.save()
        return instance


class DataPlatformForm(forms.ModelForm):
    class Meta:
        model = DataPlatform
        fields = ['name', 'image', 'platform_type']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > 2 * 1024 * 1024:
            raise forms.ValidationError('Image must be smaller than 2 MB.')
        if image and not image.content_type.startswith('image/'):
            raise forms.ValidationError('Please upload an image file.')
        return image
