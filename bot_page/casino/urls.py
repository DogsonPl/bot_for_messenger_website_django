from django.urls import path

from . import views

app_name = "casino"

urlpatterns = [
    path('', views.index, name='index'),
    path("set_daily", views.set_daily, name="set_daily"),
    path("set_daily_fb", views.set_daily_fb, name="set_daily_fb"),
    path("set_daily_dm", views.set_daily_dm, name="set_daily_dm"),
    path("bet", views.make_bet, name="bet"),
    path("bet_fb", views.make_bet_fb, name="bet_fb"),
    path("bet_dm", views.make_bet_dm, name="bet_dm"),
    path("jackpot_buy", views.jackpot_buy, name="jackpot_buy"),
    path("jackpot_buy_fb", views.jackpot_buy_fb, name="jackpot_buy_fb"),
    path("jackpot_buy_dm", views.jackpot_buy_dm, name="jackpot_buy_dm"),
    path("buy_scratch_card", views.buy_scratch_card, name="buy_scratch_card"),
    path("buy_scratch_card_fb", views.buy_scratch_card_fb, name="buy_scratch_card_fb"),
    path("buy_scratch_card_dm", views.buy_scratch_card_dm, name="buy_scratch_card_dm"),
    path("create_account", views.create_account_fb, name="create_account"),
    path("create_account_dm", views.create_account_dm, name="create_account_dm"),
    path("shop", views.shop, name="shop"),
    path("shop_fb", views.shop_fb, name="shop_fb"),
    path("shop_dm", views.shop_dm, name="shop_dm"),
    path("slots", views.slots, name="slots"),
    path("slots_fb", views.slots_fb, name="slots_fb"),
    path("slots_dm", views.slots_fb, name="slots_dm"),
    path("connect_mail_with_fb", views.connect_mail_with_fb, name="connect_mail_with_fb"),
    path("connect_mail_with_dogsonki_app", views.connect_mail_with_dogsonki_app, name="connect_mail_with_dogsonki_app")
]
