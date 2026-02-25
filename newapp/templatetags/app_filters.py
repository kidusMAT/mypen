from django import template

register = template.Library()

@register.filter
def format_stats(value):
    try:
        num = int(value)
    except (ValueError, TypeError):
        return value

    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M+"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K+"
    
    return str(num)
