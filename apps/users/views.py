from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm, CustomUserLoginForm
from django.contrib.auth.decorators import login_required


def register(request):
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            
            phone = request.POST.get('phone', '').strip()
            newsletter = request.POST.get('newsletter') == 'on'
            
            login(request, user)
            
            messages.success(
                request, 
                f'Welcome to Vintage Lab, {user.first_name}! Your account has been created successfully.'
            )
            return redirect('users:register') 
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Invalid login credentials.')
    else:
        form = CustomUserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})
    

@login_required
def profile(request):
    """Отображение профиля пользователя"""
    return render(request, 'users/profile.html')