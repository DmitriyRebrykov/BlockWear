from django.contrib import admin
from .models import Category, Size, Product, ProductSize, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','slug','description','price','created_at','updated_at','main_image','status_discount','category']
    list_filter = ['category','color']
    search_fields = ['name']
    prepopulated_fields = {'slug':('name',)}
    inlines = [ProductImageInline, ProductSizeInline]

class CategoryAdmin(admin.ModelAdmin):
    list_display =  ['name','slug']
    prepopulated_fields = {'slug':('name',)}


class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Size, SizeAdmin)