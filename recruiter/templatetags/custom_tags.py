from django import template
from recruiter.utils import is_premium as is_premium_util

register = template.Library()

@register.filter
def is_premium(user):
    return is_premium_util(user)

@register.filter
def replace_underscore(value):
    """Replaces underscores with spaces in a string."""
    return str(value).replace('_', ' ')