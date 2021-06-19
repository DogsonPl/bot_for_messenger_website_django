from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.db.models import ObjectDoesNotExist
from hcaptcha.fields import hCaptchaField
from .models import User


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "form-control mb-2"}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"class": "form-control mb-2"}))
    captcha = hCaptchaField()

    class Meta:
        model = User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "form-control mb-2"}))
    username = forms.CharField(label="Nick", widget=forms.TextInput(attrs={"class": "form-control mb-2"}))
    password1 = forms.CharField(label="Hasło", widget=forms.PasswordInput(attrs={"class": "form-control mb-2"}))
    password2 = forms.CharField(label="Potwierdź hasło",
                                widget=forms.PasswordInput(attrs={"class": "form-control mb-2"}))
    referrer = forms.CharField(label="Wpisz tu kod referencyjny, żeby otrzymać darmowe 50 dogecoinów!",
                               max_length=12, min_length=12, required=False,
                               widget=forms.TextInput(attrs={"class": "form-control mb-2"}))
    captcha = hCaptchaField()

    class Meta:
        model = User
        fields = ["email", "password1", "password2", "username", "referrer", "captcha"]

    def is_valid(self, request):
        is_valid = super().is_valid()
        if is_valid:
            referral_code = request.POST.get("referrer")
            if not referral_code:
                return True

            try:
                User.objects.get(referral_code=referral_code)
            except ObjectDoesNotExist:
                return False
            else:
                return True
        return False


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label="Twoje stare hasło",
                                   widget=forms.PasswordInput(attrs={"class": "form-control mb-2"}))
    new_password1 = forms.CharField(label="Nowe hasło",
                                    widget=forms.PasswordInput(attrs={"class": "form-control mb-2"}))
    new_password2 = forms.CharField(label="Potwierdź hasło",
                                    widget=forms.PasswordInput(attrs={"class": "form-control mb-2"}))


class ResetPasswordEmailForm(PasswordResetForm):
    email = forms.CharField(label="Email", widget=forms.EmailInput(attrs={"class": "form-control mb-2"}),
                            max_length=100)


class ResetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label="Nowe hasło",
                                    widget=forms.PasswordInput(attrs={"class": "form-control mb-2"}))
    new_password2 = forms.CharField(label="Potwierdź hasło",
                                    widget=forms.PasswordInput(attrs={"class": "form-control mb-2"}))


class ChangeNicknameForm(forms.Form):
    new_nickname = forms.CharField(label="Twój nowy nick, zmiana kosztuje 100 dogecoinów", min_length=2, max_length=150)
