from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm, OTPForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
import random
from datetime import timedelta
from django.utils import timezone
from .models import EmailOTP, CustomUser
from django.core.mail import send_mail
from django.contrib import messages

def generate_otp():
    return f"{random.randint(100000, 999999)}"

def create_email_otp(user, purpose):
    otp = generate_otp()
    expiry_time = timezone.now() + timedelta(minutes=10)
    
    otp_record, created = EmailOTP.objects.update_or_create(
        user=user,
        purpose=purpose,
        defaults={'otp': otp, 'expires_at': expiry_time}
    )
    return otp

def verify_otp(user, otp_input, purpose):
    try:
        otp_record = EmailOTP.objects.get(user=user, purpose=purpose)
        if otp_record.otp == otp_input and not otp_record.is_expired():
            otp_record.delete() 
            return True
        return False
    except EmailOTP.DoesNotExist:
        return False


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            otp = create_email_otp(user, purpose='register')
            send_mail(
                'Your Registration OTP',
                f'Your OTP is {otp}',
                'noreply@example.com',
                [user.email],
            )
            request.session['user_id'] = user.id
            return redirect('vault:verify_otp', purpose='register')
    else:
        form = RegisterForm()
    return render(request, 'vault/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            try:
                user = CustomUser.objects.get(email=email)
                otp = create_email_otp(user, purpose='login')
                send_mail(
                    'Your Login OTP',
                    f'Your OTP is {otp}',
                    'noreply@example.com',
                    [user.email],
                )
                request.session['user_id'] = user.id
                return redirect('vault:verify_otp', purpose='login')
            except CustomUser.DoesNotExist:
                form.add_error(None, 'User with this email does not exist.')
    else:
        form = LoginForm()
    return render(request, 'vault/login.html', {'form': form})

@login_required
def dashboard_view(request):
    return render(request, 'vault/dashboard.html')

def verify_otp_view(request, purpose):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('vault:login')
    
    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_input = form.cleaned_data['otp']
            if verify_otp(user, otp_input, purpose):
                if purpose == 'register':
                    user.is_active = True
                    user.save()
                messages.success(request, f'{purpose.capitalize()} successful!')
                return redirect('vault:dashboard') 
            else:
                messages.error(request, 'Invalid or expired OTP.')
    else:
        form = OTPForm()
    return render(request, 'vault/verify_otp.html', {'form': form, 'purpose': purpose})

def resend_otp_view(request, purpose):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "No user session found. Please start again.")
        return redirect('vault:login')

    user = CustomUser.objects.get(id=user_id)
    otp = create_email_otp(user, purpose) 

    send_mail(
        f'Your {purpose.capitalize()} OTP',
        f'Your new OTP is {otp}',
        'noreply@example.com',
        [user.email],
    )
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('vault:verify_otp', purpose=purpose)
