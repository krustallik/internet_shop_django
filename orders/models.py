from decimal import Decimal
from django.conf import settings
from django.db import models
from main.models import Product


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_PAID = 'paid'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Нове'),
        (STATUS_PAID, 'Оплачене'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)

    promo_code = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PAID)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'#{self.id} {self.user} {self.final_price} грн'
