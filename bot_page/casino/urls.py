from django.urls import path

from . import views

app_name = "casino"

urlpatterns = [
    path('', views.index, name='index'),
    path("set_daily", views.set_daily, name="set_daily"),
    path("bet", views.make_bet, name="bet"),
    path("jackpot_buy", views.jackpot_buy, name="jackpot_buy")
]
