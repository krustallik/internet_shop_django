from django.shortcuts import render, get_object_or_404
from django.db.models import F, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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

    # фільтр за категорією
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)

    # пошук
    search_query = request.GET.get("q", "").strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    # сортування
    current_sort = request.GET.get("sort", "new")
    products = products.order_by(SORT_MAP.get(current_sort, "-created_at"))

    # пагінація (6 на сторінку)
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
        "main/product_list.html",  # ← під нову назву з підкресленням
        {
            "products": products_page,  # об’єкт Page
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

    return render(
        request,
        "main/product_detail.html",  # ← теж з підкресленням
        {"product": product, "related_products": related_products, "categories": categories},
    )
