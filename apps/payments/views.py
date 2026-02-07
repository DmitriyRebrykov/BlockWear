from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import stripe
import json
import logging

from apps.cart.cart import Cart
from .forms import CheckoutForm
from .models import Order, OrderItem
from apps.main.models import ProductSize

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


def calculate_shipping(cart_total):
    """Calculate shipping cost based on cart total"""
    if cart_total >= Decimal('200.00'):
        return Decimal('0.00')
    return Decimal('15.00')


def calculate_tax(subtotal, shipping):
    """Calculate tax (example: 10%)"""
    return (subtotal + shipping) * Decimal('0.10')


@require_http_methods(["GET", "POST"])
def checkout(request):
    """Checkout page with form"""
    cart = Cart(request)

    if not cart:
        messages.warning(request, 'Your cart is empty')
        return redirect('cart:cart_detail')

    # Calculate costs
    subtotal = cart.get_total_price()
    shipping_cost = calculate_shipping(subtotal)
    tax_amount = calculate_tax(subtotal, shipping_cost)
    total = subtotal + shipping_cost + tax_amount

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            try:
                # Create Stripe PaymentIntent
                intent = stripe.PaymentIntent.create(
                    amount=int(total * 100),  # Convert to cents
                    currency=settings.STRIPE_CURRENCY,
                    metadata={
                        'email': form.cleaned_data['email'],
                        'user_id': request.user.id if request.user.is_authenticated else None,
                    }
                )

                # Store form data in session
                request.session['checkout_data'] = form.cleaned_data
                request.session['payment_intent_id'] = intent.id
                request.session['order_amounts'] = {
                    'subtotal': str(subtotal),
                    'shipping': str(shipping_cost),
                    'tax': str(tax_amount),
                    'total': str(total)
                }

                return redirect('payments:payment')

            except stripe.error.StripeError as e:
                logger.error(f'Stripe error: {str(e)}')
                messages.error(request, 'Payment processing error. Please try again.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        # Pre-fill form for authenticated users
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'phone': request.user.phone or '',
                'address_line1': request.user.address1 or '',
                'address_line2': request.user.address2 or '',
                'city': request.user.city or '',
                'postal_code': request.user.postal_code or '',
                'country': request.user.country or '',
            }

        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'tax_amount': tax_amount,
        'total': total,
    }

    return render(request, 'payments/checkout.html', context)


@require_http_methods(["GET"])
def payment(request):
    """Payment page with Stripe Elements"""
    if 'checkout_data' not in request.session:
        messages.warning(request, 'Please complete checkout first')
        return redirect('cart:checkout')

    cart = Cart(request)
    checkout_data = request.session.get('checkout_data')
    order_amounts = request.session.get('order_amounts')
    payment_intent_id = request.session.get('payment_intent_id')

    # Get client secret
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        client_secret = intent.client_secret
    except stripe.error.StripeError as e:
        logger.error(f'Stripe error retrieving intent: {str(e)}')
        messages.error(request, 'Payment session expired. Please try again.')
        return redirect('payments:checkout')

    context = {
        'cart': cart,
        'checkout_data': checkout_data,
        'order_amounts': order_amounts,
        'client_secret': client_secret,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }

    return render(request, 'payments/payment.html', context)


@require_POST
def payment_success(request):
    """Handle successful payment"""
    if 'checkout_data' not in request.session:
        return redirect('main:main_page')

    try:
        cart = Cart(request)
        checkout_data = request.session.get('checkout_data')
        order_amounts = request.session.get('order_amounts')
        payment_intent_id = request.session.get('payment_intent_id')

        # Verify payment with Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if intent.status != 'succeeded':
            raise Exception('Payment not successful')

        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=checkout_data['email'],
            first_name=checkout_data['first_name'],
            last_name=checkout_data['last_name'],
            phone=checkout_data['phone'],
            address_line1=checkout_data['address_line1'],
            address_line2=checkout_data.get('address_line2', ''),
            city=checkout_data['city'],
            postal_code=checkout_data['postal_code'],
            country=checkout_data['country'],
            customer_notes=checkout_data.get('customer_notes', ''),
            total_amount=Decimal(order_amounts['total']),
            shipping_cost=Decimal(order_amounts['shipping']),
            tax_amount=Decimal(order_amounts['tax']),
            stripe_payment_intent_id=payment_intent_id,
            status='paid'
        )

        # Create order items and reduce stock
        for item in cart:
            # Получаем правильный ProductSize объект
            product_size = ProductSize.objects.get(
                product=item['product'],
                size=item['size']
            )

            OrderItem.objects.create(
                order=order,
                product=item['product'],
                size=product_size,  # ← Теперь передаем ProductSize, а не Size
                price=item['price'],
                quantity=item['quantity']
            )

            # Reduce stock
            product_size.stock -= item['quantity']
            product_size.save()

        # Clear cart and session
        cart.clear()
        del request.session['checkout_data']
        del request.session['order_amounts']
        del request.session['payment_intent_id']

        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('payments:order_confirmation', order_id=order.id)

    except Exception as e:
        logger.error(f'Order creation error: {str(e)}')
        messages.error(request, 'Error processing order. Please contact support.')
        return redirect('cart:cart_detail')


def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id)

    # Security: Only show order to owner or staff
    if request.user.is_authenticated:
        if order.user != request.user and not request.user.is_staff:
            messages.error(request, 'Access denied')
            return redirect('main:main_page')
    else:
        # For guest orders, verify email in session
        if order.email != request.session.get('guest_order_email'):
            messages.error(request, 'Access denied')
            return redirect('main:main_page')

    context = {
        'order': order,
    }

    return render(request, 'payments/order_confirmation.html', context)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error('Invalid webhook payload')
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.error('Invalid webhook signature')
        return HttpResponse(status=400)

    # Handle different event types
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_success(payment_intent)

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_payment_failure(payment_intent)

    elif event['type'] == 'charge.refunded':
        charge = event['data']['object']
        handle_refund(charge)

    return HttpResponse(status=200)


def handle_payment_success(payment_intent):
    """Handle successful payment webhook"""
    try:
        order = Order.objects.get(stripe_payment_intent_id=payment_intent['id'])
        order.status = 'paid'
        order.stripe_charge_id = payment_intent.get('latest_charge', '')
        order.save()
        logger.info(f'Order {order.id} marked as paid')
    except Order.DoesNotExist:
        logger.warning(f'Order not found for payment intent {payment_intent["id"]}')


def handle_payment_failure(payment_intent):
    """Handle failed payment webhook"""
    try:
        order = Order.objects.get(stripe_payment_intent_id=payment_intent['id'])
        order.status = 'cancelled'
        order.admin_notes = f"Payment failed: {payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')}"
        order.save()
        logger.info(f'Order {order.id} marked as cancelled due to payment failure')
    except Order.DoesNotExist:
        logger.warning(f'Order not found for failed payment intent {payment_intent["id"]}')


def handle_refund(charge):
    """Handle refund webhook"""
    try:
        order = Order.objects.get(stripe_charge_id=charge['id'])
        order.status = 'refunded'
        order.save()

        # Restore stock
        for item in order.items.all():
            product_size = ProductSize.objects.get(
                product=item.product,
                size=item.size
            )
            product_size.stock += item.quantity
            product_size.save()

        logger.info(f'Order {order.id} refunded and stock restored')
    except Order.DoesNotExist:
        logger.warning(f'Order not found for charge {charge["id"]}')