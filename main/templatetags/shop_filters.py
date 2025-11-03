from django import template
from django.utils import timezone

register = template.Library()

@register.filter(name="currency")
def format_currency(value, currency="₴"):
    """Форматує число як ціну з валютою."""
    try:
        return f"{float(value):.2f} {currency}"
    except (ValueError, TypeError):
        return value

@register.filter
def discount_percentage(original_price, discount_price):
    """Відсоток знижки (якщо треба)."""
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
    """Людинозрозумілий 'час тому'."""
    if not date:
        return ""
    now = timezone.now()
    diff = now - date
    s = diff.total_seconds()
    if s < 60:
        return "щойно"
    if s < 3600:
        return f"{int(s/60)} хв тому"
    if s < 86400:
        return f"{int(s/3600)} год тому"
    if s < 604800:
        return f"{int(s/86400)} дн тому"
    return date.strftime("%d.%m.%Y")
