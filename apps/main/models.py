from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=58)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return f'{self.name}'

class Size(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.name}'

class ProductSize(models.Model):
    size = models.ForeignKey('Size', on_delete=models.CASCADE, related_name='product_size')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)

class Product(models.Model):
    name = models.CharField(max_length=58)
    slug = models.SlugField(max_length=58, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    color = models.CharField(max_length=100)
    main_image = models.ImageField(upload_to='products/main/')

    status_discount = models.BooleanField(default=False)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name = 'products')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)



class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name = 'images')
    image = models.ImageField(upload_to='products/extra/')


from apps.main.review_models import Review, ReviewImage, ReviewHelpful
