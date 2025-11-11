from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Discount(models.Model):
    DISCOUNT_TYPE_PERCENTAGE = 'percentage'
    DISCOUNT_TYPE_FIXED = 'fixed'

    DISCOUNT_TYPE_CHOICES = (
        (DISCOUNT_TYPE_PERCENTAGE, 'Відсоток'),
        (DISCOUNT_TYPE_FIXED, 'Фіксована сума'),
    )

    product = models.ForeignKey(
        'main.Product',
        on_delete=models.CASCADE,
        related_name='discounts',
    )
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    min_quantity = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Знижка'
        verbose_name_plural = 'Знижки'

    def __str__(self):
        return f'{self.product} ({self.get_discount_type_display()} {self.value})'

    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active
            and self.start_date <= now <= self.end_date
        )

    def calculate_discount(self, price, quantity=1):
        if not self.is_valid() or quantity < self.min_quantity:
            return Decimal('0.00')

        price = Decimal(price)
        quantity = int(quantity)
        total = price * quantity

        if self.discount_type == self.DISCOUNT_TYPE_PERCENTAGE:
            discount = total * self.value / Decimal('100')
        elif self.discount_type == self.DISCOUNT_TYPE_FIXED:
            discount = self.value
            if discount > total:
                discount = total
        else:
            return Decimal('0.00')

        return discount.quantize(Decimal('0.01'))

    def get_discounted_price(self, price, quantity=1):
        price = Decimal(price)
        quantity = int(quantity)
        total = price * quantity
        discount = self.calculate_discount(price, quantity)
        result = total - discount
        if result < 0:
            result = Decimal('0.00')
        return result.quantize(Decimal('0.01'))

    def clean(self):
        errors = {}

        if self.start_date and self.end_date and self.end_date <= self.start_date:
            errors['end_date'] = 'Кінець дії має бути пізніше за початок.'

        if self.discount_type == self.DISCOUNT_TYPE_PERCENTAGE:
            if self.value is None or self.value <= 0 or self.value > 100:
                errors['value'] = 'Відсоткова знижка має бути в діапазоні (0; 100].'
        elif self.discount_type == self.DISCOUNT_TYPE_FIXED:
            if self.value is None or self.value <= 0:
                errors['value'] = 'Фіксована знижка має бути більшою за 0.'

        if self.min_quantity < 1:
            errors['min_quantity'] = 'Мінімальна кількість має бути не менше 1.'

        if errors:
            raise ValidationError(errors)


class PromoCode(models.Model):
    TYPE_PERCENTAGE = 'percentage'
    TYPE_FIXED = 'fixed'
    TYPE_FREE_SHIPPING = 'free_shipping'

    DISCOUNT_TYPE_CHOICES = (
        (TYPE_PERCENTAGE, 'Відсоток'),
        (TYPE_FIXED, 'Фіксована сума'),
        (TYPE_FREE_SHIPPING, 'Безкоштовна доставка'),
    )

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_promo_codes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоди'

    def __str__(self):
        return self.code

    def can_be_used(self):
        return self.usage_limit is None or self.used_count < self.usage_limit

    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active
            and self.start_date <= now <= self.end_date
            and self.can_be_used()
        )

    def apply_discount(self, order_amount):
        order_amount = Decimal(order_amount)

        if not self.is_valid() or order_amount < self.min_order_amount:
            return Decimal('0.00')

        if self.discount_type == self.TYPE_PERCENTAGE:
            discount = order_amount * self.value / Decimal('100')
        elif self.discount_type == self.TYPE_FIXED:
            discount = self.value if self.value < order_amount else order_amount
        elif self.discount_type == self.TYPE_FREE_SHIPPING:
            # Знижка на доставку рахується окремо; тут 0, але код фіксується.
            discount = Decimal('0.00')
        else:
            discount = Decimal('0.00')

        return discount.quantize(Decimal('0.01'))

    def increment_usage(self):
        # Викликати після успішного замовлення
        self.used_count += 1
        self.save(update_fields=['used_count'])

    def clean(self):
        errors = {}

        if self.code:
            new_code = self.code.replace(' ', '').upper()
            if len(new_code) < 4:
                errors['code'] = 'Код має містити щонайменше 4 символи без пробілів.'
            self.code = new_code

        if self.start_date and self.end_date and self.end_date <= self.start_date:
            errors['end_date'] = 'Кінець дії має бути пізніше за початок.'

        if self.discount_type == self.TYPE_PERCENTAGE:
            if self.value is None or self.value <= 0 or self.value > 100:
                errors['value'] = 'Для відсотка потрібне значення (0; 100].'
        elif self.discount_type == self.TYPE_FIXED:
            if self.value is None or self.value <= 0:
                errors['value'] = 'Для фіксованої знижки значення має бути > 0.'
        elif self.discount_type == self.TYPE_FREE_SHIPPING:
            if self.value is None:
                self.value = 0

        if self.usage_limit is not None and self.usage_limit <= 0:
            errors['usage_limit'] = 'Ліміт використань має бути більшим за 0.'

        if errors:
            raise ValidationError(errors)


class PromoCodeUsage(models.Model):
    promo_code = models.ForeignKey(
        PromoCode,
        on_delete=models.CASCADE,
        related_name='usages',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='promo_usages',
    )
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-used_at']
        verbose_name = 'Використання промокоду'
        verbose_name_plural = 'Використання промокодів'

    def __str__(self):
        return f'{self.promo_code.code} - {self.user} ({self.used_at})'
