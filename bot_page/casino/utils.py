from secrets import compare_digest
from django.http import JsonResponse
from django.contrib.auth import settings

SECRET_KEY = settings.SECRET_KEY


def check_ip(function):
    def wrapper(request):
        password = request.POST.get("django_password")
        if compare_digest(password, SECRET_KEY):
            return function(request)
        else:
            return JsonResponse({"status": "forbidden"})
    return wrapper
