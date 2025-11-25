from django.shortcuts import render, get_object_or_404
from apps.main.models import Category, Size, Product
from apps.main.filters import ProductFilter
from django.db.models import Count


def main_page(request):
    return render(request, 'main/main.html')


def product_catalog(request):
    # Получаем все товары
    products = Product.objects.all().select_related('category').prefetch_related('productsize_set__size')
    
    # Применяем фильтр
    product_filter = ProductFilter(request.GET, queryset=products)
    filtered_products = product_filter.qs
    
    # Получаем категории и размеры с количеством товаров
    categories = Category.objects.annotate(product_count=Count('products'))
    sizes = Size.objects.annotate(product_count=Count('product_size'))
    
    # Подсчитываем количество
    total_products = Product.objects.count()
    filtered_count = filtered_products.count()
    
    context = {
        'filter': product_filter,  # Передаем фильтр (он содержит форму)
        'products': filtered_products,
        'categories': categories,
        'sizes': sizes,
        'results_count': filtered_count,
        'total_products': total_products,
    }
    
    return render(request, 'main/catalog.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images', 'productsize_set__size'),
        id=id,
        slug=slug
    )
    context = {'product': product}
    return render(request, 'main/product_detail.html', context=context)


def wishlist(request):
    return render(request, 'main/wishlist.html', context={})