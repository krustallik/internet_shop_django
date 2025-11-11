from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404

from main.models import Product
from discounts.models import PromoCode, PromoCodeUsage
from .models import Order


@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # кількість з форми (або 1)
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            quantity = 1
        if quantity < 1:
            quantity = 1

        total = (product.price or Decimal('0')) * quantity

        # промокод з сесії (поклався в apply_promo_code)
        code = request.session.get('promo_code')
        discount_amount = Decimal('0.00')
        promo = None

        if code:
            try:
                promo = PromoCode.objects.get(code=code)
                discount_amount = promo.apply_discount(total)
            except PromoCode.DoesNotExist:
                promo = None
                discount_amount = Decimal('0.00')

        final = total - discount_amount
        if final < 0:
            final = Decimal('0.00')

        order = Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            total_price=total,
            discount_amount=discount_amount,
            final_price=final,
            promo_code=code or '',
            status=Order.STATUS_PAID,  # в ДЗ можна вважати оплаченим
        )

        # зафіксувати використання промокоду
        if promo and discount_amount > 0:
            PromoCodeUsage.objects.create(
                promo_code=promo,
                user=request.user,
                order_amount=total,
                discount_amount=discount_amount,
            )
            promo.increment_usage()

        # очистити промокод у сесії
        request.session.pop('promo_code', None)
        request.session.pop('promo_discount', None)

        return redirect('orders:success', order_id=order.id)

    # сторінка підтвердження (можна взагалі прибрати і одразу робити POST з detail)
    return render(request, 'orders/buy_now_confirm.html', {
        'product': product,
    })


@login_required
# orders/views.py (unchanged)
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'orders/success.html', {'order': order})
