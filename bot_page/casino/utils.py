from django.http import JsonResponse


def check_ip(function):
    def wrapper(request):
        ip = request.META.get('REMOTE_ADDR')
        if ip == "127.0.0.1":
            return function(request)
        else:
            return JsonResponse({"status": "forbidden"})
    return wrapper
