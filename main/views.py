from django.shortcuts import render, get_object_or_404
from django.db.models import F, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cart.forms import CartAddProductForm
from .models import Product, Category

SORT_MAP = {
    "new": "-created_at",
    "old": "created_at",
    "popular": "-views",
    "price_low": "price",
    "price_high": "-price",
    "name": "name",
}

def product_list(request, category_slug=None):
    categories = Category.objects.filter(is_active=True).order_by("name")
    category = None
    products = Product.objects.filter(is_available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)

    search_query = request.GET.get("q", "").strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    current_sort = request.GET.get("sort", "new")
    products = products.order_by(SORT_MAP.get(current_sort, "-created_at"))

    paginator = Paginator(products, 6)
    page = request.GET.get("page", 1)
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    return render(
        request,
        "main/product_list.html",
        {
            "products": products_page,
            "categories": categories,
            "category": category,
            "current_sort": current_sort,
            "search_query": search_query,
        },
    )

def product_detail(request, id, slug):
    categories = Category.objects.filter(is_active=True).order_by("name")
    product = get_object_or_404(Product, id=id, slug=slug, is_available=True)

    # +1 перегляд (атомарно)
    Product.objects.filter(pk=product.pk).update(views=F("views") + 1)
    product.refresh_from_db(fields=["views"])

    related_products = (
        Product.objects.filter(is_available=True, category=product.category)
        .exclude(id=product.id)
        .order_by("-created_at")[:4]
    )

    # дані для блоку відгуків
    reviews_qs = product.reviews.filter(is_active=True).select_related('author')

    ctx = {
        "product": product,
        "related_products": related_products,
        "categories": categories,
        "reviews": reviews_qs,
        "reviews_count": product.get_reviews_count(),
        "average_rating": product.get_average_rating(),
        "rating_distribution": product.get_rating_distribution(),
        "user_review": (
            reviews_qs.filter(author=request.user).first()
            if request.user.is_authenticated else None
        ),
    }

    cart_product_form = CartAddProductForm()

    return render(request, 'main/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'cart_product_form': cart_product_form,
    })
