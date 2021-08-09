from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import settings
from django.core.mail import send_mail
from django.apps import apps

from . import forms
# Create your views here.

ADMIN_EMAIL = settings.ADMIN_EMAIL
CasinoPlayers = apps.get_model("casino", "CasinoPlayers")


def index(request):
    if request.user.is_authenticated:
        player = CasinoPlayers.objects.get(user=request.user)
    else:
        player = None
    return render(request, "home/index.html", {"nav_bar": "home", "player": player})


def contact(request):
    if request.method == "POST":
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            message = request.POST.get("message") + f"\n\n Sender email: {request.POST['email']}"
            send_mail(subject=f"Wiadomość od {request.user}", message=message, from_email=request.POST["email"],
                      recipient_list=[ADMIN_EMAIL])
            return render(request, "home/thanks_for_contact.html", {"nav_bar": "contact"})
        else:
            if request.user.is_authenticated:
                player = CasinoPlayers.objects.get(user=request.user)
            else:
                player = None
            messages.info(request, "Coś poszło nie tak, spróbuj wykonać captcha")

    else:
        if request.user.is_authenticated:
            player = CasinoPlayers.objects.get(user=request.user)
            form = forms.ContactForm(initial={"email": request.user.email})
        else:
            player = None
            form = forms.ContactForm()
    return render(request, "home/contact.html", {"nav_bar": "contact", "form": form, "player": player})


def privacy_policy(request):
    return render(request, "home/privacy_policy.html")
