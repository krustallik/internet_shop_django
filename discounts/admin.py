from django.contrib import admin
from django.utils.html import format_html

from .models import Discount, PromoCode, PromoCodeUsage


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'discount_type', 'value',
        'start_date', 'end_date',
        'is_active', 'is_valid_now', 'min_quantity',
    )
    list_filter = ('discount_type', 'is_active', 'start_date')
    search_fields = ('product__name', 'description')
    readonly_fields = ('created_at',)
    list_editable = ('is_active',)
    date_hierarchy = 'start_date'
    actions = ('activate_discounts', 'deactivate_discounts')

    @admin.display(boolean=True, description='Діє зараз')
    def is_valid_now(self, obj):
        return obj.is_valid()

    @admin.action(description='Активувати обрані знижки')
    def activate_discounts(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Деактивувати обрані знижки')
    def deactivate_discounts(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'discount_type', 'value',
        'usage_progress', 'valid_period',
        'is_active', 'created_by',
    )
    list_filter = ('discount_type', 'is_active', 'created_at')
    search_fields = ('code', 'description')
    readonly_fields = ('used_count', 'created_at')
    fieldsets = (
        ('Основне', {
            'fields': ('code', 'discount_type', 'value', 'description'),
        }),
        ('Обмеження', {
            'fields': ('start_date', 'end_date', 'usage_limit', 'min_order_amount'),
        }),
        ('Стан', {
            'fields': ('is_active', 'used_count', 'created_by', 'created_at'),
        }),
    )
    actions = ('activate_codes', 'deactivate_codes', 'reset_usage')

    @admin.display(description='Використання')
    def usage_progress(self, obj):
        if not obj.usage_limit:
            return f'{obj.used_count}'
        percent = int(obj.used_count / obj.usage_limit * 100)
        return format_html(
            '<div style="width:120px;border:1px solid #ddd;">'
            '<div style="width:{}%;height:8px;background:#22c55e;"></div>'
            '</div> {} / {}',
            percent, obj.used_count, obj.usage_limit
        )

    @admin.display(description='Період')
    def valid_period(self, obj):
        return f'{obj.start_date} — {obj.end_date}'

    @admin.action(description='Активувати обрані')
    def activate_codes(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Деактивувати обрані')
    def deactivate_codes(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description='Скинути лічильник')
    def reset_usage(self, request, queryset):
        queryset.update(used_count=0)


@admin.register(PromoCodeUsage)
class PromoCodeUsageAdmin(admin.ModelAdmin):
    list_display = ('promo_code', 'user', 'order_amount', 'discount_amount', 'used_at')
    list_filter = ('used_at', 'promo_code')
    search_fields = ('user__username', 'promo_code__code')
    readonly_fields = ('promo_code', 'user', 'order_amount', 'discount_amount', 'used_at')
    date_hierarchy = 'used_at'
