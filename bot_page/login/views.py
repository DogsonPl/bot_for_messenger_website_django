from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponse
from django.apps import apps
from django.db.models import ObjectDoesNotExist

from .forms import LoginForm, RegisterForm, ChangeNicknameForm
from . import utils
# Create your views here.

User = get_user_model()
CasinoPlayers = apps.get_model("casino", "CasinoPlayers")


def login_(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = request.POST["email"]
            password = request.POST["password"]
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                messages.error(request, "Hasło albo email jest niepoprawne")
    else:
        form = LoginForm()
    return render(request, "login/login.html", {"nav_bar": "account", "form": form})


def register_(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        user_mail = request.POST["email"]
        try:
            user = User.objects.get(email=user_mail)
        except ObjectDoesNotExist:
            if form.is_valid() and "+" not in user_mail and "." not in user_mail[0:-4]:
                utils.send_account_activation_email(request, form, user_mail)
                return render(request, "login/waiting_for_confirmation.html", {"nav_bar": "account", "mail": user_mail})
            else:
                messages.error(request, "Hasła się nie zgadzają, albo mail na który chcesz założyć konto nie spełnia wymagań (spróbuj usunąć '.' w środku maila jeśli posiada), założ konto na np gmailu")
        else:
            if user.is_active:
                messages.error(request, "Konto z takim mailem istnieje")
            else:
                utils.send_account_activation_email(request, form, user_mail)
                return render(request, "login/waiting_for_confirmation.html", {"nav_bar": "account", "mail": user_mail})
    else:
        form = RegisterForm()
    return render(request, "login/register.html", {"nav_bar": "account", "form": form})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except ObjectDoesNotExist:
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        # after confirming email, create or connect to player account
        utils.create_casino_player_account(user)
        login(request, user)
        return redirect("/")
    else:
        return HttpResponse("Niepoprawny link aktywacyjny")


def logout_(request):
    logout(request)
    return redirect("/")


def user_settings(request):
    if request.user.is_authenticated:
        player = CasinoPlayers.objects.get(user=request.user)
        return render(request, "login/account_settings.html", {"nav_bar": "account", "player": player})
    else:
        return redirect("account/login")


def change_nickname(request):
    if request.user.is_authenticated:
        player = CasinoPlayers.objects.get(user=request.user)
        if request.method == "POST":
            form = ChangeNicknameForm(request.POST)
            if form.is_valid():
                if player.money < 100:
                    messages.error(request, "Nie masz wystarczająco dogecoinów")
                else:
                    utils.change_player_nickname(request, player)
        else:
            form = ChangeNicknameForm()
        return render(request, "login/change_nickname.html", {"nav_bar": "account", "form": form, "player": player})
    else:
        return redirect("account/login")
