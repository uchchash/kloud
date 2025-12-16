from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, LoginForm, OTPForm, MemberForm, EmailChangeRequestForm, PasswordChangeRequestForm, UserUpdateForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
import random
from datetime import timedelta, datetime
from django.db.models import Max
from django.utils import timezone
from .models import EmailOTP, CustomUser, Member
from django.db.models import Max
from payment.models import SubscriptionPlan, UserSubscription
from django.core.mail import send_mail
from django.contrib import messages
from storage.models import Folder, File
from django.db.models import Sum

def get_or_create_member(user):
    try:
        member = user.member
    except Exception:
        member = Member.objects.create(user=user)
    
    if not member.current_plan:
        free_plan = SubscriptionPlan.objects.filter(name="Free").first()
        if free_plan:
            subscription = UserSubscription.objects.create(
                user=user,
                subscription_plan=free_plan,
                status='active',
                billing_cycle='monthly'
            )
            member.current_plan = subscription
            member.save()
            
    return member

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
    user = request.user
    get_or_create_member(user) 
    folders = Folder.objects.filter(user=user, parent=None).order_by('-updated_at')
    files = File.objects.filter(user=user, folder=None).order_by('-updated_at') 
    total_files_count = File.objects.filter(user=user).count()
    total_folders_count = Folder.objects.filter(user=user).count()
    storage_used_bytes = 0
    for file in File.objects.filter(user=user):
        try:
            storage_used_bytes += file.file.size
        except:
            pass

    def format_size(size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"
    
    member = get_or_create_member(user)
    
    storage_used = format_size(storage_used_bytes)
    
    storage_total_bytes = 0
    if member.current_plan and member.current_plan.subscription_plan:
        storage_total_bytes = member.current_plan.subscription_plan.storage_bytes()
    else:
        storage_total_bytes = 2 * 1024 * 1024 * 1024 

    storage_total = format_size(storage_total_bytes)
    storage_percentage = min(100, (storage_used_bytes / storage_total_bytes) * 100) if storage_total_bytes > 0 else 0
    
    recent_date = timezone.now() - timedelta(days=7)
    recent_activity = File.objects.filter(user=user, updated_at__gte=recent_date).count()
    
    context = {
        'folders': folders,
        'files': files,
        'total_files': total_files_count,
        'total_folders': total_folders_count,
        'storage_used': storage_used,
        'storage_total': storage_total,
        'storage_percentage': storage_percentage,
        'recent_activity': recent_activity,
        'member': member, # Pass member to context if needed for template
    }
    
    return render(request, 'vault/dashboard.html', context)

@login_required
def folder_view(request, permalink):    
    user = request.user
    get_or_create_member(user)
    folder = get_object_or_404(Folder, permalink=permalink, user=user)
    subfolders = Folder.objects.filter(user=user, parent=folder).order_by('-updated_at')
    files = File.objects.filter(user=user, folder=folder).order_by('-updated_at')
    breadcrumbs = []
    current = folder
    while current:
        breadcrumbs.insert(0, current)
        current = current.parent
    
    context = {
        'folder': folder,
        'folders': subfolders,
        'files': files,
        'breadcrumbs': breadcrumbs,
    }
    
    return render(request, 'vault/folder.html', context)


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
                    get_or_create_member(user) 
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                elif purpose == 'login':
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                elif purpose == 'change_email':
                    new_email = request.session.get('updated_email')
                    if new_email:
                        user.email = new_email
                        user.save()
                        del request.session['updated_email']
                    else:
                        messages.error(request, 'Session expired. Please try again.')
                        return redirect('vault:change_email')
                elif purpose == 'change_password':
                    new_password = request.session.get('new_password')
                    if new_password:
                        user.set_password(new_password)
                        user.save()
                        user.backend = 'django.contrib.auth.backends.ModelBackend'
                        login(request, user) 
                        del request.session['new_password']
                    else:
                        messages.error(request, 'Session expired. Please try again.')
                        return redirect('vault:change_password')
                        
                messages.success(request, f'{purpose.replace("_", " ").capitalize()} successful!')
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



@login_required
def change_email_view(request):
    if request.method == 'POST':
        form = EmailChangeRequestForm(request.POST)
        if form.is_valid():
            user = request.user
            new_email = form.cleaned_data['updated_email']
            
            request.session['updated_email'] = new_email
            
            otp = create_email_otp(user, purpose='change_email')
            send_mail(
                'Your Email Change OTP',
                f'Your OTP is {otp}',
                'noreply@example.com',
                [user.email],
            )
            request.session['user_id'] = user.id
            return redirect('vault:verify_otp', purpose='change_email')
    else:
        form = EmailChangeRequestForm()
    return render(request, 'vault/change_email.html', {'form': form})

@login_required
def update_profile_view(request):
    member = get_or_create_member(request.user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        member_form = MemberForm(request.POST, request.FILES, instance=member)
        if user_form.is_valid() and member_form.is_valid():
            user_form.save()
            member_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('vault:dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        member_form = MemberForm(instance=member)
    return render(request, 'vault/update_profile.html', {'user_form': user_form, 'member_form': member_form})

@login_required
def profile_view(request):
    member = get_or_create_member(request.user)
    plan = member.current_plan
    name = request.user.first_name + " " + request.user.last_name
    
    can_upgrade = False
    can_downgrade = False
    
    if plan:
        current_tier = plan.subscription_plan.tier_order
        max_tier = SubscriptionPlan.objects.aggregate(Max('tier_order'))['tier_order__max'] or 0
        
        can_upgrade = current_tier < max_tier
        can_downgrade = current_tier > 0
    
    return render(request, 'vault/profile.html', {
        'member': member,
        'plan': plan,
        'user': request.user,
        'name': name,
        'can_upgrade': can_upgrade,
        'can_downgrade': can_downgrade
    })

@login_required
def plans_view(request):
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('tier_order')
    return render(request, 'vault/plans.html', {'plans': plans})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeRequestForm(request.POST)
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data['new_password']
            
            request.session['new_password'] = new_password
            
            otp = create_email_otp(user, purpose='change_password')
            send_mail(
                'Your Password Change OTP',
                f'Your OTP is {otp}',
                'noreply@example.com',
                [user.email],
            )
            return redirect('vault:verify_otp', purpose='change_password')
    else:
        form = PasswordChangeRequestForm()
    return render(request, 'vault/change_password.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('vault:login')
