from django.shortcuts import render, get_object_or_404
from apps.main.models import Category, Size, Product
from apps.main.filters import ProductFilter
from django.db.models import Count, Avg, Q
from apps.main.review_models import Review  # ← ЭТО ВАЖНО


def main_page(request):
    return render(request, 'main/main.html')


def product_catalog(request):
    products = Product.objects.all().select_related('category').prefetch_related('productsize_set__size')
    
    product_filter = ProductFilter(request.GET, queryset=products)
    filtered_products = product_filter.qs
    
    categories = Category.objects.annotate(product_count=Count('products'))
    sizes = Size.objects.annotate(product_count=Count('product_size'))
    
    total_products = Product.objects.count()
    filtered_count = filtered_products.count()
    
    context = {
        'filter': product_filter,
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
    
    # Статистика отзывов
    stats = Review.objects.filter(product=product).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id'),
        rating_5=Count('id', filter=Q(rating=5)),
        rating_4=Count('id', filter=Q(rating=4)),
        rating_3=Count('id', filter=Q(rating=3)),
        rating_2=Count('id', filter=Q(rating=2)),
        rating_1=Count('id', filter=Q(rating=1)),
    )
    
    context = {
        'product': product,
        'stats': stats,
    }
    return render(request, 'main/product_detail.html', context=context)


def wishlist(request):
    return render(request, 'main/wishlist.html', context={})