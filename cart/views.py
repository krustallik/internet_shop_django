from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from main.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from discounts.models import PromoCode

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override'],
        )
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)

    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True,
        })

    cart_total = cart.get_total_price()

    promo_code = request.session.get('promo_code')
    promo_discount = Decimal('0')
    final_total = cart_total
    promo_obj = None

    if promo_code:
        try:
            promo_obj = PromoCode.objects.get(code=promo_code)
            promo_discount = promo_obj.apply_discount(cart_total)
            if promo_discount > 0:
                final_total = cart_total - promo_discount
            else:
                # якщо вже не валідний — прибираємо
                request.session.pop('promo_code', None)
                promo_code = None
        except PromoCode.DoesNotExist:
            request.session.pop('promo_code', None)
            promo_code = None

    context = {
        'cart': cart,
        'cart_total': cart_total,
        'final_total': final_total,
        'promo_code': promo_code,
        'promo_discount': promo_discount,
    }
    return render(request, 'cart/cart_detail.html', context)