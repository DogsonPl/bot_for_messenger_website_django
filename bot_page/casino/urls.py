from django.urls import path

from . import views

app_name = "casino"

urlpatterns = [
    path('', views.index, name='index'),
    path("set_daily", views.set_daily, name="set_daily"),
    path("set_daily_fb", views.set_daily_fb, name="set_daily_fb"),
    path("bet", views.make_bet, name="bet"),
    path("bet_fb", views.make_bet_fb, name="bet_fb"),
    path("jackpot_buy", views.jackpot_buy, name="jackpot_buy"),
    path("jackpot_buy_fb", views.jackpot_buy_fb, name="jackpot_buy_fb"),
    path("buy_scratch_card", views.buy_scratch_card, name="buy_scratch_card"),
    path("buy_scratch_card_fb", views.buy_scratch_card_fb, name="buy_scratch_card_fb"),
    path("create_account", views.create_account_fb, name="create_account")
]
