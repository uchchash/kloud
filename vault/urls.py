from django.urls import path, include
from .views import register_view, login_view, dashboard_view, verify_otp_view, resend_otp_view, folder_view, change_email_view, change_password_view, logout_view
from .views import profile_view, update_profile_view, plans_view
app_name = 'vault'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('folder/<str:permalink>/', folder_view, name='folder'),
    path('<str:purpose>/verify-otp/', verify_otp_view, name='verify_otp'),
    path('<str:purpose>/resend-otps/', resend_otp_view, name='resend_otp'),
    path('change-email/', change_email_view, name='change_email'),
    path('change-password/', change_password_view, name='change_password'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/update/', update_profile_view, name='update_profile'),
    path('plans/', plans_view, name='plans'),
]

