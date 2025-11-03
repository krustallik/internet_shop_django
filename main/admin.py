# main/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "is_active", "image_tag")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active",)

    @admin.display(description="Зображення")
    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:6px;" />',
                obj.image.url,
            )
        return "—"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "price",
        "is_available",
        "featured",
        "views",
        "image_tag",
    )
    list_filter = ("category", "is_available", "featured", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("price", "is_available", "featured")
    ordering = ("-created_at",)

    def get_queryset(self, request):
        # оптимізація для списку
        qs = super().get_queryset(request)
        return qs.select_related("category")

    @admin.display(description="Зображення")
    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:6px;" />',
                obj.image.url,
            )
        return "—"
