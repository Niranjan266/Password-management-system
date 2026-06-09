from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
import json
from .models import PasswordEntry, CATEGORY_CHOICES
from .forms import RegisterForm, LoginForm, PasswordEntryForm

QUICK_PLATFORMS = [
    ('Google', 'social', '🔵'), ('Gmail', 'email', '📧'), ('GitHub', 'dev', '🐙'),
    ('GitLab', 'dev', '🦊'), ('Facebook', 'social', '📘'), ('Instagram', 'social', '📸'),
    ('Twitter', 'social', '🐦'), ('LinkedIn', 'work', '💼'), ('Microsoft', 'work', '🪟'),
    ('Outlook', 'email', '📨'), ('AWS', 'cloud', '☁️'), ('Azure', 'cloud', '🔷'),
    ('Dropbox', 'cloud', '📦'), ('Notion', 'work', '📝'), ('Slack', 'work', '💬'),
    ('Discord', 'social', '🎮'), ('Apple', 'other', '🍎'), ('Spotify', 'streaming', '🎵'),
    ('Netflix', 'streaming', '🎬'), ('PayPal', 'finance', '💳'),
    ('TeamViewer', 'remote', '🖥️'), ('AnyDesk', 'remote', '🖥️'),
    ('RDP', 'remote', '💻'), ('VNC', 'remote', '🔌'), ('SSH', 'remote', '⌨️'),
    ('Zoom', 'work', '📹'), ('Figma', 'work', '🎨'), ('Jira', 'work', '📋'),
]

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'vault/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'vault/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    entries = PasswordEntry.objects.filter(user=request.user)
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    if search:
        entries = entries.filter(Q(platform__icontains=search) | Q(username__icontains=search))
    if category:
        entries = entries.filter(category=category)
    favorites = entries.filter(is_favorite=True)
    stats = {
        'total': PasswordEntry.objects.filter(user=request.user).count(),
        'favorites': PasswordEntry.objects.filter(user=request.user, is_favorite=True).count(),
        'categories': len(set(PasswordEntry.objects.filter(user=request.user).values_list('category', flat=True))),
    }
    return render(request, 'vault/dashboard.html', {
        'entries': entries, 'favorites': favorites,
        'stats': stats, 'categories': CATEGORY_CHOICES,
        'search': search, 'active_category': category,
    })

@login_required
def add_entry(request):
    if request.method == 'POST':
        form = PasswordEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, f'"{entry.platform}" saved to vault!')
            return redirect('dashboard')
    else:
        form = PasswordEntryForm()
    return render(request, 'vault/entry_form.html', {'form': form, 'title': 'Add Password', 'categories': CATEGORY_CHOICES, 'quick_platforms': QUICK_PLATFORMS})

@login_required
def edit_entry(request, pk):
    entry = get_object_or_404(PasswordEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PasswordEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{entry.platform}" updated!')
            return redirect('dashboard')
    else:
        initial = {'password': entry.password}
        form = PasswordEntryForm(instance=entry, initial=initial)
    return render(request, 'vault/entry_form.html', {'form': form, 'title': 'Edit Password', 'entry': entry, 'categories': CATEGORY_CHOICES, 'quick_platforms': QUICK_PLATFORMS})

@login_required
def delete_entry(request, pk):
    entry = get_object_or_404(PasswordEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        name = entry.platform
        entry.delete()
        messages.success(request, f'"{name}" removed from vault.')
    return redirect('dashboard')

@login_required
def get_password(request, pk):
    entry = get_object_or_404(PasswordEntry, pk=pk, user=request.user)
    return JsonResponse({'password': entry.password, 'username': entry.username})

@login_required
@require_POST
def toggle_favorite(request, pk):
    entry = get_object_or_404(PasswordEntry, pk=pk, user=request.user)
    entry.is_favorite = not entry.is_favorite
    entry.save()
    return JsonResponse({'is_favorite': entry.is_favorite})
