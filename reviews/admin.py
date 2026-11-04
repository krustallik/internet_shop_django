from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'product', 'rating', 'title_preview', 'created_at', 'is_active', 'helpful_count')
    list_filter = ('rating', 'is_active', 'created_at')
    search_fields = ('author__username', 'product__name', 'title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)
    fieldsets = (
        ('Review details', {'fields': ('product', 'author', 'rating', 'title', 'content', 'advantages', 'disadvantages')}),
        ('Status', {'fields': ('is_active', 'helpful_count', 'created_at', 'updated_at')}),
    )

    @admin.display(description='Title')
    def title_preview(self, obj):
        return (obj.title[:50] + '…') if len(obj.title) > 50 else obj.title

    actions = ['activate_reviews', 'deactivate_reviews']

    def activate_reviews(self, request, queryset):
        queryset.update(is_active=True)
    activate_reviews.short_description = 'Activate selected reviews'

    def deactivate_reviews(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_reviews.short_description = 'Deactivate selected reviews'
