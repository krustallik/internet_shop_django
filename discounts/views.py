from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from main.models import Product
from .forms import DiscountForm, PromoCodeForm, ApplyPromoCodeForm
from .models import Discount, PromoCode, PromoCodeUsage
from cart.cart import Cart

def product_discounts(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    discounts = [d for d in product.discounts.all() if d.is_valid()]
    best_discount = None
    discounted_price = None

    if discounts:
        best_discount = min(discounts,
                            key=lambda d: d.get_discounted_price(product.price, 1))
        discounted_price = best_discount.get_discounted_price(product.price, 1)

    return render(request, 'discounts/product_discounts.html', {
        'product': product,
        'discounts': discounts,
        'best_discount': best_discount,
        'discounted_price': discounted_price,
    })


@staff_member_required
def add_discount(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.product = product
            discount.save()
            messages.success(request, 'Знижку створено.')
            return redirect('main:product_detail', id=product.id, slug=product.slug)
    else:
        form = DiscountForm()

    return render(request, 'discounts/add_discount.html', {
        'form': form,
        'product': product,
    })


@staff_member_required
def edit_discount(request, discount_id):
    discount = get_object_or_404(Discount, id=discount_id)
    product = discount.product

    if request.method == 'POST':
        form = DiscountForm(request.POST, instance=discount)
        if form.is_valid():
            form.save()
            messages.success(request, 'Знижку оновлено.')
            return redirect('main:product_detail', id=product.id, slug=product.slug)
    else:
        form = DiscountForm(instance=discount)

    return render(request, 'discounts/edit_discount.html', {
        'form': form,
        'product': product,
        'discount': discount,
    })


@staff_member_required
def delete_discount(request, discount_id):
    discount = get_object_or_404(Discount, id=discount_id)
    product = discount.product
    discount.delete()
    messages.success(request, 'Знижку видалено.')
    return redirect('main:product_detail', id=product.id, slug=product.slug)


@staff_member_required
def create_promo_code(request):
    if request.method == 'POST':
        form = PromoCodeForm(request.POST)
        if form.is_valid():
            promo = form.save(commit=False)
            if not promo.created_by:
                promo.created_by = request.user
            promo.save()
            messages.success(request, 'Промокод створено.')
            return redirect('discounts:promo_code_list')
    else:
        form = PromoCodeForm()

    return render(request, 'discounts/create_promo_code.html', {'form': form})


@staff_member_required
def promo_code_list(request):
    qs = list(PromoCode.objects.all())

    status = request.GET.get('status')
    search = (request.GET.get('q') or '').upper()

    if status == 'active':
        qs = [p for p in qs if p.is_valid()]
    elif status == 'inactive':
        qs = [p for p in qs if not p.is_valid()]

    if search:
        qs = [p for p in qs if search in p.code]

    return render(request, 'discounts/promo_code_list.html', {
        'promo_codes': qs,
        'status': status,
        'search': search,
    })


@login_required
def apply_promo_code(request):
    if request.method != 'POST':
        return HttpResponseForbidden('Тільки POST')

    form = ApplyPromoCodeForm(request.POST)
    if not form.is_valid():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        for errors in form.errors.values():
            for e in errors:
                messages.error(request, e)
        return redirect(request.META.get('HTTP_REFERER', '/'))

    code = form.cleaned_data['promo_code']
    promo = get_object_or_404(PromoCode, code=code)

    # 1) якщо є order_amount з форми — беремо його
    raw_amount = request.POST.get('order_amount')

    if raw_amount is not None:
        try:
            order_amount = Decimal(raw_amount)
        except Exception:
            order_amount = Decimal('0')
    else:
        # 2) інакше вважаємо, що це кошик
        cart = Cart(request)
        order_amount = cart.get_total_price()

    discount_amount = promo.apply_discount(order_amount)

    if discount_amount <= 0:
        msg = 'Промокод не може бути застосований до цієї суми замовлення.'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # зберігаємо код у сесії, суму можемо перераховувати динамічно в кошику
    request.session['promo_code'] = promo.code

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'code': promo.code,
            'discount': str(discount_amount),
            'new_total': str(order_amount - discount_amount),
        })

    messages.success(request, f'Промокод {promo.code} застосовано.')
    return redirect(request.META.get('HTTP_REFERER', '/'))


def remove_promo_code(request):
    request.session.pop('promo_code', None)
    request.session.pop('promo_discount', None)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, 'Промокод видалено.')
    return redirect(request.META.get('HTTP_REFERER', '/'))


@staff_member_required
def promo_code_stats(request, code_id):
    promo = get_object_or_404(PromoCode, id=code_id)
    usages = promo.usages.select_related('user').all()
    total_discount = usages.aggregate(total=Sum('discount_amount'))['total'] or Decimal('0.00')

    return render(request, 'discounts/promo_code_stats.html', {
        'promo': promo,
        'usages': usages,
        'total_discount': total_discount,
    })
