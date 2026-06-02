from django import template

register = template.Library()

@register.filter(name='split_email')
def split_email(value):
    if not value:
        return ""
    return value.split('@')[0]
