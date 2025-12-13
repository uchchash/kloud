from django.urls import path, include
from .views import register_view, login_view, dashboard_view

app_name = 'vault'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
]
