from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import logout, login, authenticate, get_user_model
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.apps import apps
from django.db.models import ObjectDoesNotExist
from .forms import LoginForm, RegisterForm

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
                return redirect("/", {"nav_bar": ""})
            else:
                messages.error(request, "Hasło albo email jest niepoprawne")
    else:
        form = LoginForm()
    return render(request, "login/login.html", {"nav_bar": "account", "form": form})


def register_(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user_mail = request.POST["email"]
            user.save()
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
            # todo automatyczne przekierowane do logowania po zaakceptowaniu linku
            response = render(request, "login/waiting_for_confirmation.html", {"nav_bar": "account", "mail": user_mail})
            response.set_cookie("username", request.POST["username"])
            return response
        else:
            messages.error(request, "Hasła się nie zgadzają, albo wpisałeś złego maila")
    else:
        username = request.COOKIES.get("username")
        if username is not None:
            try:
                User.objects.get(username=username).delete()
            except User.DoesNotExist:
                pass
        form = RegisterForm(initial={"username": username})
    response = render(request, "login/register.html", {"nav_bar": "account", "form": form})
    response.delete_cookie("username")
    return response


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        # after confirming email, create or connect to player account
        try:
            player = CasinoPlayers.objects.get(email=user.email)
        except ObjectDoesNotExist:
            CasinoPlayers.objects.create(user=user, email=user.email)
        else:
            player.user = user
            player.save()
        return HttpResponse("Konto zostało aktywowane")
    else:
        return HttpResponse("Niepoprawny link aktywacyjny")


def logout_(request):
    logout(request)
    return redirect("/", {"nav_bar": "home"})


def user_settings(request):
    if request.user.is_authenticated:
        player = CasinoPlayers.objects.get(user=request.user)
        return render(request, "login/account_settings.html", {"nav_bar": "account", "player": player})
    else:
        return redirect("account/login")
