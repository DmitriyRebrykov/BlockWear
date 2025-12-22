from django.urls import path
from apps.main import review_views

app_name = 'reviews'

urlpatterns = [
    path('product/<int:product_id>/reviews/', review_views.review_list, name='review_list'),
    path('product/<int:product_id>/review/create/', review_views.review_create, name='review_create'),
    path('review/<int:review_id>/edit/', review_views.review_edit, name='review_edit'),
    path('review/<int:review_id>/delete/', review_views.review_delete, name='review_delete'),
    path('review/<int:review_id>/helpful/', review_views.review_helpful, name='review_helpful'),
    path('review/image/<int:image_id>/delete/', review_views.review_image_delete, name='review_image_delete'),
]