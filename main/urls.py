from django.urls import path
from .views import main_page,catalog


app_name = 'main'


urlpatterns = [
    path('',main_page, name='main_page'),
    path('catalog',catalog, name='catalog'),
]
