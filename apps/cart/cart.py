from decimal import Decimal
from django.conf import settings
from apps.main.models import Product, ProductSize


class Cart:
    def __init__(self, request):
        """
        Инициализация корзины
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, size_id, quantity=1, update_quantity=False):
        """
        Добавить товар в корзину или обновить его количество
        """
        product_id = str(product.id)
        size_id = str(size_id)
        cart_key = f"{product_id}_{size_id}"
        
        if cart_key not in self.cart:
            self.cart[cart_key] = {
                'product_id': product_id,
                'size_id': size_id,
                'quantity': 0,
                'price': str(product.price)
            }
        
        if update_quantity:
            self.cart[cart_key]['quantity'] = quantity
        else:
            self.cart[cart_key]['quantity'] += quantity
        
        self.save()

    def save(self):
        """
        Сохранить корзину в сессии
        """
        self.session.modified = True

    def remove(self, product_id, size_id):
        """
        Удалить товар из корзины
        """
        cart_key = f"{product_id}_{size_id}"
        if cart_key in self.cart:
            del self.cart[cart_key]
            self.save()

    def __iter__(self):
        """
        Перебор элементов корзины и получение товаров из БД
        """
        product_ids = [item['product_id'] for item in self.cart.values()]
        products = Product.objects.filter(id__in=product_ids)
        
        cart = self.cart.copy()
        
        for item in cart.values():
            product_id = int(item['product_id'])
            size_id = int(item['size_id'])
            
            item['product'] = products.get(id=product_id)
            
            # Получаем информацию о размере
            try:
                product_size = ProductSize.objects.select_related('size').get(
                    product_id=product_id,
                    size_id=size_id
                )
                item['size'] = product_size.size
                item['stock'] = product_size.stock
            except ProductSize.DoesNotExist:
                item['size'] = None
                item['stock'] = 0
            
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Подсчитать общее количество товаров в корзине
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчитать общую стоимость товаров в корзине
        """
        return sum(Decimal(item['price']) * item['quantity'] 
                   for item in self.cart.values())

    def clear(self):
        """
        Очистить корзину
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def get_item_count(self):
        """
        Получить количество уникальных позиций в корзине
        """
        return len(self.cart)