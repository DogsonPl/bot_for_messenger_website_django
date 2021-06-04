from django import forms
from hcaptcha.fields import hCaptchaField


class ContactForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=100,
                             widget=forms.EmailInput(attrs={"class": "form-control"}))
    message = forms.CharField(label="Wiadomość", max_length=10000, min_length=10,
                              widget=forms.Textarea(attrs={"class": "form-control mb-2"}))
    captcha = hCaptchaField()
