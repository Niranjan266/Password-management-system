from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
import json
from .models import DataPlatform, PasswordEntry, CATEGORY_CHOICES
from .forms import DataPlatformForm, RegisterForm, LoginForm, PasswordEntryForm

QUICK_PLATFORMS = [
    ('Google', 'social', 'google.com'), ('Gmail', 'email', 'mail.google.com'), ('GitHub', 'dev', 'github.com'),
    ('GitLab', 'dev', 'gitlab.com'), ('Facebook', 'social', 'facebook.com'), ('Instagram', 'social', 'instagram.com'),
    ('Twitter', 'social', 'x.com'), ('LinkedIn', 'work', 'linkedin.com'), ('Microsoft', 'work', 'microsoft.com'),
    ('Outlook', 'email', 'outlook.live.com'), ('AWS', 'cloud', 'aws.amazon.com'), ('Azure', 'cloud', 'azure.microsoft.com'),
    ('Dropbox', 'cloud', 'dropbox.com'), ('Notion', 'work', 'notion.so'), ('Slack', 'work', 'slack.com'),
    ('Discord', 'social', 'discord.com'), ('Apple', 'other', 'apple.com'), ('Spotify', 'streaming', 'spotify.com'),
    ('Netflix', 'streaming', 'netflix.com'), ('PayPal', 'finance', 'paypal.com'),
    ('TeamViewer', 'remote', 'teamviewer.com'), ('AnyDesk', 'remote', 'anydesk.com'),
    ('RDP', 'remote', 'microsoft.com'), ('VNC', 'remote', 'realvnc.com'), ('SSH', 'remote', 'openssh.com'),
    ('Zoom', 'work', 'zoom.us'), ('Figma', 'work', 'figma.com'), ('Jira', 'work', 'atlassian.com'),
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
        form = PasswordEntryForm(request.POST, request.FILES)
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
        form = PasswordEntryForm(request.POST, request.FILES, instance=entry)
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
        if entry.logo:
            entry.logo.delete(save=False)
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


@login_required
def data_spaces(request):
    platforms = DataPlatform.objects.filter(user=request.user)
    return render(request, 'vault/data_spaces.html', {'platforms': platforms})


@login_required
def create_data_platform(request):
    if request.method == 'POST':
        form = DataPlatformForm(request.POST, request.FILES)
        if form.is_valid():
            platform = form.save(commit=False)
            platform.user = request.user
            if platform.platform_type == 'sheet':
                platform.sheet_data = [['', '', ''], ['', '', ''], ['', '', '']]
            platform.save()
            messages.success(request, f'"{platform.name}" created!')
            return redirect('edit_data_platform', pk=platform.pk)
    else:
        form = DataPlatformForm()
    return render(request, 'vault/data_platform_form.html', {'form': form})


@login_required
def edit_data_platform(request, pk):
    platform = get_object_or_404(DataPlatform, pk=pk, user=request.user)
    if request.method == 'POST':
        if platform.platform_type == 'note':
            platform.note_content = request.POST.get('note_content', '')
        else:
            try:
                sheet_data = json.loads(request.POST.get('sheet_data', '[]'))
                if not isinstance(sheet_data, list):
                    raise ValueError
                platform.sheet_data = sheet_data
            except (json.JSONDecodeError, ValueError):
                messages.error(request, 'The sheet data could not be saved.')
                return redirect('edit_data_platform', pk=platform.pk)
        platform.save()
        messages.success(request, f'"{platform.name}" saved!')
        return redirect('edit_data_platform', pk=platform.pk)
    return render(request, 'vault/data_platform_editor.html', {'platform': platform})


@login_required
@require_POST
def delete_data_platform(request, pk):
    platform = get_object_or_404(DataPlatform, pk=pk, user=request.user)
    name = platform.name
    if platform.image:
        platform.image.delete(save=False)
    platform.delete()
    messages.success(request, f'"{name}" deleted.')
    return redirect('data_spaces')
