from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from main.models import Product
from discounts.models import PromoCode, PromoCodeUsage
from .models import Order


@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Read the requested quantity, falling back to one.
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            quantity = 1
        if quantity < 1:
            quantity = 1

        total = (product.price or Decimal('0')) * quantity

        # Apply the promo code stored in the session, if still valid.
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
            status=Order.STATUS_NEW,
        )

        # Record the demo promo usage.
        if promo and discount_amount > 0:
            PromoCodeUsage.objects.create(
                promo_code=promo,
                user=request.user,
                order_amount=total,
                discount_amount=discount_amount,
            )
            promo.increment_usage()

        # Clear the session promo code after recording the demo order.
        request.session.pop('promo_code', None)
        request.session.pop('promo_discount', None)

        return redirect('orders:success', order_id=order.id)

    # Show a demo confirmation page before creating the sample order record.
    return render(request, 'orders/buy_now_confirm.html', {
        'product': product,
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'orders/success.html', {'order': order})
