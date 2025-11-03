from django import template
from main.models import Product

register = template.Library()

@register.simple_tag
def get_products_count(category=None):
    """Кількість доступних товарів (опц. у категорії)."""
    qs = Product.objects.filter(is_available=True)
    if category:
        qs = qs.filter(category=category)
    return qs.count()

@register.simple_tag
def calculate_total(price, quantity):
    """Обчислює загальну вартість."""
    try:
        return float(price) * int(quantity)
    except (ValueError, TypeError):
        return 0

@register.simple_tag(takes_context=True)
def user_greeting(context):
    """Привітання користувача з контексту."""
    user = context.get("user")
    if user and user.is_authenticated:
        return f"Вітаємо, {user.username}!"
    return "Вітаємо, гість!"

# Inclusion-tag: показ картки товару, використовує існуючий компонент
@register.inclusion_tag("main/components/product_card.html")
def show_product_card(p):
    """Відображає картку товару (передає 'p' у компонент)."""
    return {"p": p}
