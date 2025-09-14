from django.urls import path
from .views import main_page,product_catalog,product_detail


app_name = 'main'


urlpatterns = [
    path('',main_page, name='main_page'),
    path('catalog',product_catalog, name='product_catalog'),
    path('product-detail', product_detail, name='product_detail'),
]
