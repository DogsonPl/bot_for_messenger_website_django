from math import floor

from django import template

register = template.Library()


@register.filter
def format_money(num):
    try:
        formatted_money = floor(num*100)/100
    except TypeError:
        formatted_money = num
    return formatted_money
