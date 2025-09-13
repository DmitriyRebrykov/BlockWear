from django.shortcuts import render

from apps.main.models import Category, Size, Product


def main_page(request):
    return render(request,'main/main.html')

def catalog(request):
    categories = Category.objects.all()
    sizes = Size.objects.all()
    products = Product.objects.all()
    return render(request, 'main/catalog.html',{'categories':categories, 'sizes':sizes, 'products': products })

def product_detail(request):
    return render(request, 'main/product_detail.html')