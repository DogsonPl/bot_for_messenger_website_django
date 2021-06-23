from django import template

register = template.Library()


@register.filter
def add(num1, num2):
    adding_result = num1+num2
    return "%.2f" % adding_result
