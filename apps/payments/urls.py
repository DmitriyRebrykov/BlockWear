from django.urls import path
from .views import (
    checkout, payment, payment_success, order_confirmation, stripe_webhook
)

app_name = 'payments'

urlpatterns = [
    # Checkout & Payment
    path('checkout/', checkout, name='checkout'),
    path('payment/', payment, name='payment'),
    path('payment/success/', payment_success, name='payment_success'),
    path('order/<int:order_id>/confirmation/', order_confirmation, name='order_confirmation'),

    # Stripe webhook
    path('webhook/stripe/', stripe_webhook, name='stripe_webhook'),
]