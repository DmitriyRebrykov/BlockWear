from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser
import re


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-field__input',
                'placeholder': ' ',
                'autocomplete': 'email',
                'id': 'id_email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-field__input',
                'placeholder': ' ',
                'autocomplete': 'given-name',
                'id': 'id_first_name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-field__input',
                'placeholder': ' ',
                'autocomplete': 'family-name',
                'id': 'id_last_name'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Настройка виджетов для полей password1 и password2
        self.fields['password1'].widget.attrs.update({
            'class': 'form-field__input',
            'placeholder': ' ',
            'autocomplete': 'new-password',
            'id': 'id_password1'
        })
        
        self.fields['password2'].widget.attrs.update({
            'class': 'form-field__input',
            'placeholder': ' ',
            'autocomplete': 'new-password',
            'id': 'id_password2'
        })
        
        # Убираем стандартные help_text
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        
        # Делаем поля обязательными
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean_email(self):
        """Проверка уникальности и валидности email"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('Email обязателен для заполнения.')
        
        # Нормализация email
        email = email.lower().strip()
        
        # Проверка существования email
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже зарегистрирован.')
        
        # Дополнительная проверка формата
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError('Введите корректный email адрес.')
        
        # Проверка на одноразовые email (опционально)
        disposable_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com', 'mailinator.com']
        domain = email.split('@')[1]
        if domain in disposable_domains:
            raise ValidationError('Использование одноразовых email адресов запрещено.')
        
        return email

    def clean_first_name(self):
        """Валидация имени"""
        first_name = self.cleaned_data.get('first_name')
        
        if not first_name:
            raise ValidationError('Имя обязательно для заполнения.')
        
        first_name = first_name.strip()
        
        # Проверка на минимальную длину
        if len(first_name) < 2:
            raise ValidationError('Имя должно содержать минимум 2 символа.')
        
        # Проверка на максимальную длину
        if len(first_name) > 50:
            raise ValidationError('Имя не должно превышать 50 символов.')
        
        # Проверка на допустимые символы
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁіІїЇєЄґҐ\s\-\']+$', first_name):
            raise ValidationError('Имя может содержать только буквы, пробелы, дефисы и апострофы.')
        
        # Проверка на подозрительные паттерны
        if re.search(r'(.)\1{4,}', first_name):
            raise ValidationError('Имя содержит недопустимую последовательность символов.')
        
        return first_name.title()

    def clean_last_name(self):
        """Валидация фамилии"""
        last_name = self.cleaned_data.get('last_name')
        
        if not last_name:
            raise ValidationError('Фамилия обязательна для заполнения.')
        
        last_name = last_name.strip()
        
        # Проверка на минимальную длину
        if len(last_name) < 2:
            raise ValidationError('Фамилия должна содержать минимум 2 символа.')
        
        # Проверка на максимальную длину
        if len(last_name) > 50:
            raise ValidationError('Фамилия не должна превышать 50 символов.')
        
        # Проверка на допустимые символы
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁіІїЇєЄґҐ\s\-\']+$', last_name):
            raise ValidationError('Фамилия может содержать только буквы, пробелы, дефисы и апострофы.')
        
        # Проверка на подозрительные паттерны
        if re.search(r'(.)\1{4,}', last_name):
            raise ValidationError('Фамилия содержит недопустимую последовательность символов.')
        
        return last_name.title()

    def clean_password1(self):
        """Дополнительная валидация пароля"""
        password1 = self.cleaned_data.get('password1')
        
        if password1:
            # Проверка минимальной длины
            if len(password1) < 8:
                raise ValidationError('Пароль должен содержать минимум 8 символов.')
            
            # Проверка на наличие букв
            if not re.search(r'[A-Za-z]', password1):
                raise ValidationError('Пароль должен содержать хотя бы одну букву.')
            
            # Проверка на наличие цифр
            if not re.search(r'\d', password1):
                raise ValidationError('Пароль должен содержать хотя бы одну цифру.')
            
            # Проверка на общие пароли
            common_passwords = [
                'password', '12345678', 'qwerty', 'abc123', 
                'password1', '11111111', 'password123', 'qwerty123'
            ]
            if password1.lower() in common_passwords:
                raise ValidationError('Этот пароль слишком распространенный. Выберите более надежный пароль.')
            
            # Проверка на последовательности
            if re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde)', password1.lower()):
                raise ValidationError('Пароль не должен содержать простые последовательности.')
        
        return password1

    def clean(self):
        """Общая валидация формы"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        email = cleaned_data.get('email')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        # Проверка, что пароль не содержит email
        if email and password1:
            email_username = email.split('@')[0].lower()
            if len(email_username) >= 4 and email_username in password1.lower():
                self.add_error('password1', 'Пароль не должен содержать части вашего email адреса.')

        # Проверка, что пароль не содержит имя или фамилию
        if first_name and password1:
            if len(first_name) >= 4 and first_name.lower() in password1.lower():
                self.add_error('password1', 'Пароль не должен содержать ваше имя.')

        if last_name and password1:
            if len(last_name) >= 4 and last_name.lower() in password1.lower():
                self.add_error('password1', 'Пароль не должен содержать вашу фамилию.')

        return cleaned_data

    def save(self, commit=True):
        """Сохранение пользователя"""
        user = super().save(commit=False)
        
        # Дополнительная настройка пользователя
        user.email = self.cleaned_data['email'].lower()
        user.first_name = self.cleaned_data['first_name'].title()
        user.last_name = self.cleaned_data['last_name'].title()
        
        if commit:
            user.save()
        
        return user
        
class CustomUserLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)

    def clean(self):
        """Проверка данных формы"""
        cleaned_data = super().clean()
        
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if not email or not password:
            raise forms.ValidationError('Пожалуйста, заполните все поля.')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError('Пользователь с таким email не найден.')
        
        if not user.check_password(password):
            raise forms.ValidationError('Неверный пароль.')
        
        return cleaned_data

    def save(self):
        """Сохранение пользователя"""
        user = super().save(commit=False)
        
        # Дополнительная настройка пользователя
        user.email = self.cleaned_data['email'].lower()
        user.first_name = self.cleaned_data['first_name'].title()
        user.last_name = self.cleaned_data['last_name'].title()
        
        if commit:
            user.save()
        
        return user
        
