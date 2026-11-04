from django import template
from main.models import Product

register = template.Library()

@register.simple_tag
def get_products_count(category=None):
    """Count available products, optionally within a category."""
    qs = Product.objects.filter(is_available=True)
    if category:
        qs = qs.filter(category=category)
    return qs.count()

@register.simple_tag
def calculate_total(price, quantity):
    """Calculate a simple price-by-quantity total."""
    try:
        return float(price) * int(quantity)
    except (ValueError, TypeError):
        return 0

@register.simple_tag(takes_context=True)
def user_greeting(context):
    """Return a short English greeting for the current user."""
    user = context.get("user")
    if user and user.is_authenticated:
        return f"Welcome, {user.username}!"
    return "Welcome, guest!"

# Inclusion tag for a shared product card.
@register.inclusion_tag("main/components/product_card.html")
def show_product_card(p):
    """Render the shared product card component."""
    return {"p": p}
