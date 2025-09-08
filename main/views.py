from django.shortcuts import render

from main.models import Category, Size


def main_page(request):
    return render(request,'main/main.html')

def catalog(request):
    categories = Category.objects.all()
    sizes = Size.objects.all()
    return render(request, 'main/catalog.html',{'categories':categories, 'sizes':sizes})

def product_detail(request):
    return render(request, 'main/product_detail.html')