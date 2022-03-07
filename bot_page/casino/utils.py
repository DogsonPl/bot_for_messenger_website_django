from secrets import compare_digest
from math import floor
from datetime import datetime, timedelta
import pytz

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
        return JsonResponse({"message": "forbidden"})
    return wrapper


def format_money(num):
    """:returns rounded number to lower (2 digits)"""
    formatted_money = floor(num*100)/100
    return formatted_money


def count_scratch_card_timeout(player, minutes) -> str:
    try:
        return str(player.last_time_scratch + timedelta(minutes=minutes) - datetime.now(tz=pytz.timezone(settings.TIME_ZONE)))[2:7]
    except TypeError:
        return ""


def check_boost_time(time):
    if time.days < 0:
        return "Nie kupione", False
    return f"Boost będzie działał jeszcze przez {str(time).split('.')[0]} (trzeba odświeżyć strone żeby odświeżyć czas)", True
