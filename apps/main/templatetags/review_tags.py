from django import template
from apps.main.review_models import ReviewHelpful

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if dictionary:
        return dictionary.get(key)
    return None

@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """Divide value by arg"""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0

@register.simple_tag
def get_user_review(user, product):
    """Get user's review for a product"""
    from apps.main.review_models import Review
    if user.is_authenticated:
        return Review.objects.filter(user=user, product=product).first()
    return None

@register.filter(name='has_user_marked_helpful')
def has_user_marked_helpful(user, review):
    """Check if user has marked review as helpful"""
    if not user.is_authenticated:
        return False
    return ReviewHelpful.objects.filter(user=user, review=review).exists()