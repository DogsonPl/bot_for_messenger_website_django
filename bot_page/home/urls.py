from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    path('', views.index, name='index'),
    path("kontakt", views.contact, name="contact"),
    path("privacy_policy", views.privacy_policy, name="privacy_policy"),
    path("spotify_connect", views.spotify_connect, name="spotify_connect"),
    path("spotify_connected", views.spotipy_connected, name="spotify_connected")
]
