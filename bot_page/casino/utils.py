from secrets import compare_digest
from math import floor

from django.http import JsonResponse
from django.contrib.auth import settings

SECRET_KEY = settings.SECRET_KEY


def check_post_password(function):
    def wrapper(request):
        password = request.POST.get("django_password")
        try:
            if compare_digest(password, SECRET_KEY):
                return function(request)
        except TypeError:
            pass
        return JsonResponse({"status": "forbidden"})
    return wrapper


def format_money(num):
    """:returns rounded number to lower (2 digits)"""
    formatted_money = floor(num*100)/100
    return formatted_money
