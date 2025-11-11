from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .forms import ReviewForm
from .models import Review
from main.models import Product

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if Review.objects.filter(product=product, author=request.user).exists():
        messages.warning(request, 'Ви вже залишали відгук до цього товару.')
        return redirect('main:product_detail', id=product.id, slug=product.slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.author = request.user
            review.save()
            messages.success(request, 'Відгук опубліковано.')
            return redirect('main:product_detail', id=product.id, slug=product.slug)
    else:
        form = ReviewForm()

    return render(request, 'reviews/add_review.html', {'form': form, 'product': product})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden('Недостатньо прав.')

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Відгук оновлено.')
            return redirect('main:product_detail', id=review.product.id, slug=review.product.slug)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'reviews/edit_review.html', {'form': form, 'product': review.product})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden('Недостатньо прав.')

    if request.method == 'POST':
        product = review.product
        review.delete()
        messages.success(request, 'Відгук видалено.')
        return redirect('main:product_detail', id=product.id, slug=product.slug)

    # просте підтвердження через POST
    return HttpResponseRedirect(reverse('main:product_detail', kwargs={'id': review.product.id, 'slug': review.product.slug}))

def mark_helpful(request, review_id):
    review = get_object_or_404(Review, id=review_id, is_active=True)
    review.helpful_count = (review.helpful_count or 0) + 1
    review.save(update_fields=['helpful_count'])
    return redirect(request.META.get('HTTP_REFERER', reverse('main:product_detail', kwargs={'id': review.product.id, 'slug': review.product.slug})))
