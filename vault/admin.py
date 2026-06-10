from django.contrib import admin
from .models import DataPlatform, PasswordEntry

admin.site.register(PasswordEntry)
admin.site.register(DataPlatform)
