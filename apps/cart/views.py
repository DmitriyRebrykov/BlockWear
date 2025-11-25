from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from .cart import Cart
from apps.main.models import Product, ProductSize


def cart_detail(request):
    """
    Страница корзины
    """
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    """
    Добавление товара в корзину
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    size_id = request.POST.get('size_id')
    quantity = int(request.POST.get('quantity', 1))
    
    if not size_id:
        messages.error(request, 'Выберите размер')
        return redirect('product_detail', slug=product.slug)
    
    # Проверяем наличие товара
    try:
        product_size = ProductSize.objects.get(product=product, size_id=size_id)
        if product_size.stock < quantity:
            messages.error(request, f'Недостаточно товара на складе. Доступно: {product_size.stock}')
            return redirect('product_detail', slug=product.slug)
    except ProductSize.DoesNotExist:
        messages.error(request, 'Выбранный размер недоступен')
        return redirect('product_detail', slug=product.slug)
    
    cart.add(product=product, size_id=size_id, quantity=quantity)
    messages.success(request, f'{product.name} добавлен в корзину')
    
    return redirect('cart_detail')


@require_POST
def cart_remove(request, product_id, size_id):
    """
    Удаление товара из корзины
    """
    cart = Cart(request)
    cart.remove(product_id, size_id)
    messages.success(request, 'Товар удален из корзины')
    return redirect('cart_detail')


@require_POST
def cart_update(request, product_id, size_id):
    """
    Обновление количества товара в корзине
    """
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    
    # Проверяем наличие
    try:
        product_size = ProductSize.objects.get(product_id=product_id, size_id=size_id)
        if product_size.stock < quantity:
            messages.error(request, f'Недостаточно товара. Доступно: {product_size.stock}')
            return redirect('cart_detail')
    except ProductSize.DoesNotExist:
        messages.error(request, 'Товар не найден')
        return redirect('cart_detail')
    
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product, size_id=size_id, quantity=quantity, update_quantity=True)
    
    return redirect('cart_detail')


def cart_clear(request):
    """
    Очистка корзины
    """
    cart = Cart(request)
    cart.clear()
    messages.success(request, 'Корзина очищена')
    return redirect('cart_detail')