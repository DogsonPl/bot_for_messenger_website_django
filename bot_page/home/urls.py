from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    path('', views.index, name='index'),
    path("kontakt", views.contact, name="contact"),
    path("privacy_policy", views.privacy_policy, name="privacy_policy")
]
