from django.apps import apps
from django.db.models import ObjectDoesNotExist
from django.db.utils import IntegrityError, OperationalError
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import User

CasinoPlayers = apps.get_model("casino", "CasinoPlayers")


def create_casino_player_account(user):
    try:
        player = CasinoPlayers.objects.get(email=user.email)
    except ObjectDoesNotExist:
        CasinoPlayers.objects.create(user=user, email=user.email)
    else:
        player.user = user
        player.save()


def send_account_activation_email(request, form, user_mail):
    try:
        user = form.save(commit=False)
        user.is_active = False
        user.save()
    except ValueError:
        # if user is created, but requested second confirmation email, don`t create user account second time
        user = User.objects.get(email=user_mail)
    site = get_current_site(request)
    html_template = get_template("login/activate_email.html")
    context = {"domain": site.domain,
               "uid": urlsafe_base64_encode(force_bytes(user.pk)),
               "token": default_token_generator.make_token(user),
               "username": request.POST["username"]}
    html_message = html_template.render(context)
    email = EmailMultiAlternatives("Mail potwierdzający stworzenie konta", to=[user_mail])
    email.attach_alternative(html_message, "text/html")
    email.send()


def change_player_nickname(request, player):
    new_nickname = request.POST["new_nickname"]
    request.user.username = new_nickname
    try:
        request.user.save()
    except IntegrityError:
        messages.error(request, "Ten nick jest obecnie w użyciu")
    except OperationalError:
        messages.error(request, "Użyłeś nieprawidłowego znaku (najprawdopodobniej emotki)")
    else:
        player.money -= 100
        player.save()
        messages.success(request, f"Zmieniono nick na {new_nickname}")
