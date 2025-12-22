from django.contrib import admin
from .models import Category, Size, Product, ProductSize, ProductImage
from .review_models import Review, ReviewImage, ReviewHelpful


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
    list_display = ['id','name']


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0
    readonly_fields = ['uploaded_at']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'user', 'rating', 'title', 'is_verified_purchase', 'helpful_count', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['title', 'content', 'user__email', 'product__name']
    readonly_fields = ['created_at', 'updated_at', 'helpful_count']
    inlines = [ReviewImageInline]
    date_hierarchy = 'created_at'

class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__title', 'user__email']
    readonly_fields = ['created_at']


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(ReviewHelpful, ReviewHelpfulAdmin)