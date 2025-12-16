from django.urls import path
from .views import register, profile, login

app_name = 'users'


urlpatterns = [
    path('register', register, name='register'),
    path('login', login, name='login'),
    path('profile', profile, name='profile'),
]
