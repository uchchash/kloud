from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'vault/dashboard.html')
    else:
        form = RegisterForm()
    return render(request, 'vault/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('vault:dashboard')
    else:
        form = LoginForm()
    return render(request, 'vault/login.html', {'form': form})

@login_required
def dashboard_view(request):
    return render(request, 'vault/dashboard.html')