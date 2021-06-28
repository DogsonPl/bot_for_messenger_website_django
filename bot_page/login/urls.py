from django.urls import path

from . import views

app_name = "account"

urlpatterns = [
    path("login", views.login_, name='login'),
    path("logout", views.logout_, name='logout'),
    path("register", views.register_, name="register"),
    path("activate/<uidb64>/<token>", views.activate, name="activate"),
    path("settings", views.user_settings, name="settings"),
    path("change_nickname", views.change_nickname, name="change_nickname")
]
