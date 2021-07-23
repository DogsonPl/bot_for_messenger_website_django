from math import floor

from django import template

register = template.Library()


@register.filter
def format_money(num):
    formatted_money = floor(num*100)/100
    return formatted_money
