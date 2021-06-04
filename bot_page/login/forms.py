from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from hcaptcha.fields import hCaptchaField

User = get_user_model()


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
    captcha = hCaptchaField()

    class Meta:
        model = User
        fields = ["email", "password1", "password2", "username", "captcha"]


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
