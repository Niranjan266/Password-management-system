from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_entry, name='add_entry'),
    path('edit/<int:pk>/', views.edit_entry, name='edit_entry'),
    path('delete/<int:pk>/', views.delete_entry, name='delete_entry'),
    path('password/<int:pk>/', views.get_password, name='get_password'),
    path('favorite/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
]
