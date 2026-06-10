from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from cryptography.fernet import Fernet
import base64
import hashlib
from urllib.parse import quote, urlparse

def get_fernet():
    key = settings.VAULT_ENCRYPTION_KEY.encode()
    key = base64.urlsafe_b64encode(hashlib.sha256(key).digest())
    return Fernet(key)

CATEGORY_CHOICES = [
    ('social', 'Social Media'),
    ('dev', 'Developer Tools'),
    ('email', 'Email'),
    ('finance', 'Finance & Banking'),
    ('work', 'Work & Productivity'),
    ('remote', 'Remote Desktop'),
    ('cloud', 'Cloud Storage'),
    ('shopping', 'Shopping'),
    ('streaming', 'Streaming'),
    ('other', 'Other'),
]

PLATFORM_ICONS = {
    'Google': '🔵', 'Gmail': '📧', 'GitHub': '🐙', 'GitLab': '🦊',
    'Facebook': '📘', 'Instagram': '📸', 'Twitter': '🐦', 'LinkedIn': '💼',
    'Microsoft': '🪟', 'Outlook': '📨', 'AWS': '☁️', 'Azure': '🔷',
    'Dropbox': '📦', 'Notion': '📝', 'Slack': '💬', 'Discord': '🎮',
    'Apple': '🍎', 'Spotify': '🎵', 'Netflix': '🎬', 'PayPal': '💳',
    'TeamViewer': '🖥️', 'AnyDesk': '🖥️', 'RDP': '💻', 'VNC': '🔌',
    'SSH': '⌨️', 'Zoom': '📹', 'Figma': '🎨', 'Jira': '📋',
}

class PasswordEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='passwords')
    platform = models.CharField(max_length=100)
    logo = models.FileField(upload_to='password_logos/', blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    username = models.CharField(max_length=200)
    _password = models.TextField(db_column='password')
    url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def password(self):
        try:
            f = get_fernet()
            return f.decrypt(self._password.encode()).decode()
        except:
            return self._password

    @password.setter
    def password(self, value):
        f = get_fernet()
        self._password = f.encrypt(value.encode()).decode()

    @property
    def icon(self):
        for key, icon in PLATFORM_ICONS.items():
            if key.lower() in self.platform.lower():
                return icon
        return '🔐'

    @property
    def logo_image_url(self):
        if self.logo:
            return self.logo.url
        if self.logo_url:
            return self.logo_url

        if self.url:
            domain = urlparse(self.url).netloc
        else:
            domain = self.platform.lower().replace(' ', '') + '.com'
        return f"https://www.google.com/s2/favicons?domain={quote(domain)}&sz=128"

    @property
    def category_color(self):
        colors = {
            'social': '#8B5CF6', 'dev': '#10B981', 'email': '#3B82F6',
            'finance': '#F59E0B', 'work': '#6366F1', 'remote': '#EF4444',
            'cloud': '#06B6D4', 'shopping': '#EC4899', 'streaming': '#F97316',
            'other': '#6B7280'
        }
        return colors.get(self.category, '#6B7280')

    def __str__(self):
        return f"{self.platform} - {self.username}"

    class Meta:
        ordering = ['-updated_at']


class DataPlatform(models.Model):
    PLATFORM_TYPES = [
        ('note', 'Notepad'),
        ('sheet', 'Sheet'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_platforms')
    name = models.CharField(max_length=100)
    image = models.FileField(upload_to='platform_images/', blank=True, null=True)
    platform_type = models.CharField(max_length=20, choices=PLATFORM_TYPES, default='note')
    note_content = models.TextField(blank=True)
    sheet_data = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_platform_type_display()})"

    class Meta:
        ordering = ['-updated_at']
