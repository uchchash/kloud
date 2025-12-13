from django.urls import path, include
from .views import register_view, login_view, dashboard_view, verify_otp_view, resend_otp_view

app_name = 'vault'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('<str:purpose>/verify-otp/', verify_otp_view, name='verify_otp'),
    path('<str:purpose>/resend-otps/', resend_otp_view, name='resend_otp'),
]
