from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required


def register(request):
    # if request.user.is_authenticated:
    #     return redirect('users:register')  # или другая страница
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            # Сохраняем пользователя
            user = form.save()
            
            # Получаем дополнительные данные из формы
            phone = request.POST.get('phone', '').strip()
            newsletter = request.POST.get('newsletter') == 'on'
            
            # Можно сохранить дополнительные данные, если нужно
            # user.phone = phone
            # user.newsletter_subscribed = newsletter
            # user.save()
            
            # Автоматический вход после регистрации
            login(request, user)
            
            messages.success(
                request, 
                f'Welcome to Vintage Lab, {user.first_name}! Your account has been created successfully.'
            )
            return redirect('users:register')  # или другая страница после регистрации
        else:
            # Выводим ошибки
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})
    
@login_required
def profile(request):
    """Отображение профиля пользователя"""
    return render(request, 'users/profile.html')