from django.shortcuts import render

from apps.main.forms import ProductFilterForm
from apps.main.models import Category, Size, Product
from django.db.models import Count

def main_page(request):
    return render(request,'main/main.html')

def product_catalog(request):
    categories = Category.objects.annotate(product_count=Count('products'))
    sizes = Size.objects.annotate(product_count=Count('product_size'))
    products = Product.objects.all()

    form = ProductFilterForm(request.GET or None, categories=categories, sizes=sizes)

    if request.method == 'GET' and form.is_valid():
        if form.cleaned_data['categories']:
            products = products.filter(category__id__in=form.cleaned_data['categories'])
        if form.cleaned_data['eras']:
            products = products.filter(era__in=form.cleaned_data['eras'])
        if form.cleaned_data['sizes']:
            products = products.filter(productsize__size__id__in=form.cleaned_data['sizes']).distinct()
        if form.cleaned_data['conditions']:
            products = products.filter(condition__in=form.cleaned_data['conditions'])
        if form.cleaned_data['price_max']:
            products = products.filter(price__lte=form.cleaned_data['price_max'])

    total_products = Product.objects.count()
    filtered_count = products.count()

    context = {
        'form': form,
        'products': products,
        'categories': categories,
        'sizes': sizes,
        'results_count': filtered_count,
        'total_products': total_products,
    }

    return render(request, 'main/catalog.html', context)

def product_detail(request):
    return render(request, 'main/product_detail.html')