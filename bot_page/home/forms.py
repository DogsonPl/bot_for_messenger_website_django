from django import forms
from hcaptcha.fields import hCaptchaField


class ContactForm(forms.Form):
    email = forms.EmailField(label="<p>Email</p>", max_length=100,
                             widget=forms.EmailInput(attrs={"class": "form-control mb-3"}))
    message = forms.CharField(label="<p>Wiadomość</p>", max_length=10000, min_length=10,
                              widget=forms.Textarea(attrs={"class": "form-control mb-3"}))
    captcha = hCaptchaField()
