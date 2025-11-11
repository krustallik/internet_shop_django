from decimal import Decimal
from django.conf import settings
from main.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Додаємо товар в кошик.
        Ціна, яка зберігається, вже з урахуванням знижки (якщо є).
        """
        product_id = str(product.id)

        # ціна з урахуванням знижки (твій Product вже має ці методи/властивості)
        try:
            has_discount = product.has_active_discount
        except AttributeError:
            has_discount = False

        if has_discount:
            unit_price = product.get_discounted_price  # твоя властивість
        else:
            unit_price = product.price

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(unit_price),          # ціна в кошику
                'original_price': str(product.price),  # для відображення стара ціна
            }

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        if self.cart[product_id]['quantity'] <= 0:
            del self.cart[product_id]

        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Додаємо в елементи реальний product, перетворюємо ціни в Decimal,
        рахуємо total_price.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            if 'original_price' in item:
                item['original_price'] = Decimal(item['original_price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        self.session.pop(settings.CART_SESSION_ID, None)
        self.save()
