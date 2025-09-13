from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("apps.main.urls")),
    path('cart', include("apps.cart.urls")),
    path('users/', include("apps.users.urls")),
]
