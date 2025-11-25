from django.urls import path
from .views import main_page,product_catalog,product_detail,wishlist


app_name = 'main'


urlpatterns = [
    path('',main_page, name='main_page'),
    path('catalog',product_catalog, name='product_catalog'),
    path('wishlist', wishlist, name='wishlist'),
    path('<int:id>/<slug:slug>', product_detail, name='product_detail'),
]
