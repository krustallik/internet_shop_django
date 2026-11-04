from .models import Category


def navigation(request):
    """Expose the small active category set to the shared site header."""
    return {
        "navigation_categories": Category.objects.filter(is_active=True).order_by("name")[:6],
    }
