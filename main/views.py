from django.shortcuts import render, get_object_or_404
from django.db.models import F
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

    sort = request.GET.get("sort", "new")
    products = products.order_by(SORT_MAP.get(sort, "-created_at"))

    context = {
        "products": products,
        "categories": categories,
        "category": category,
        "current_sort": sort,
    }
    return render(request, "main/product-list.html", context)


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

    return render(
        request,
        "main/product-detail.html",
        {"product": product, "related_products": related_products, "categories": categories},
    )
