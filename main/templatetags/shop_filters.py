from django import template
from django.utils import timezone

register = template.Library()

@register.filter(name="currency")
def format_currency(value, currency="₴"):
    """Format a number as a price with the selected currency symbol."""
    try:
        return f"{float(value):.2f} {currency}"
    except (ValueError, TypeError):
        return value

@register.filter
def discount_percentage(original_price, discount_price):
    """Return the percentage difference between two prices."""
    try:
        original = float(original_price)
        discount = float(discount_price)
        if original <= 0:
            return 0
        return int(((original - discount) / original) * 100)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def compact_number(value):
    """1000→1.0K, 1500000→1.5M."""
    try:
        value = int(value)
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        if value >= 1_000:
            return f"{value/1_000:.1f}K"
        return str(value)
    except (ValueError, TypeError):
        return value

@register.filter
def time_ago(date):
    """Return a compact English relative timestamp."""
    if not date:
        return ""
    now = timezone.now()
    diff = now - date
    s = diff.total_seconds()
    if s < 60:
        return "just now"
    if s < 3600:
        return f"{int(s/60)} min ago"
    if s < 86400:
        return f"{int(s/3600)} hr ago"
    if s < 604800:
        return f"{int(s/86400)} days ago"
    return date.strftime("%b %d, %Y")
