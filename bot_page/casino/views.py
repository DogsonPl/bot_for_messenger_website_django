from datetime import datetime

from django.contrib.auth import settings
from django.db import transaction
from django.db.models import Sum, ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pytz

from .models import CasinoPlayers, BetsHistory, Jackpot
from .forms import BetForm, JackpotForm
from .utils import check_post_password, format_money, count_scratch_card_timeout
from . import casino_actions


FB_REGISTER_ACCOUNT_MESSAGE = "💡 Użyj polecenia !register żeby móc się bawić w kasyno. Wszystkie dogecoiny są sztuczne"


class EmptyBet:
    date = ""
    amount = ""
    user_number = ""
    drown_number = ""
    win = ""

    def __iter__(self):
        yield self


def index(request):
    if request.user.is_authenticated:
        player = CasinoPlayers.objects.get(user=request.user)
        last_bets = BetsHistory.objects.all().order_by("-id")
        user_bets = last_bets.filter(player=player)[:10]
        if len(user_bets) == 0:
            user_bets = EmptyBet
        last_bets = last_bets[:10]

        try:
            total_tickets = int(Jackpot.objects.aggregate(total=Sum("tickets"))["total"])
        except TypeError:
            total_tickets = 0

        try:
            user_tickets = Jackpot.objects.get(player=player)
        except ObjectDoesNotExist:
            user_tickets = 0
        else:
            user_tickets = user_tickets.tickets

        bet_form = BetForm(initial={"bet_money": 0})
        jackpot_form = JackpotForm(initial={"tickets": 0})
        if player.faster_scratch_time > datetime.now(tz=pytz.timezone(settings.TIME_ZONE)):
            minutes = 10
        else:
            minutes = 20
        scratch_timeout = count_scratch_card_timeout(player, minutes)

        return render(request, "casino/index.html", {"nav_bar": "casino",
                                                     "bet_form": bet_form,
                                                     "jackpot_form": jackpot_form,
                                                     "player": player,
                                                     "user_bets": user_bets,
                                                     "last_bets": last_bets,
                                                     "total_tickets": total_tickets,
                                                     "user_tickets": user_tickets,
                                                     "scratch_timeout": scratch_timeout})
    else:
        # todo demo page
        return redirect("account:login")


def set_daily(request):
    if request.method == "POST" and request.user.is_authenticated:
        player = CasinoPlayers.objects.get(user=request.user)
        message = casino_actions.set_daily(player)
        return JsonResponse({"player_money": format_money(player.money), "daily_strike": player.daily_strike, "received": message})
    else:
        return JsonResponse({"status": "forbidden"})


@csrf_exempt
@check_post_password
def set_daily_fb(request):
    try:
        player = CasinoPlayers.objects.get(user_fb_id=request.POST["fb_user_id"])
    except ObjectDoesNotExist:
        message = FB_REGISTER_ACCOUNT_MESSAGE
    else:
        message = casino_actions.set_daily(player)
    return JsonResponse({"message": message})


def make_bet(request):
    if request.method == "POST" and request.user.is_authenticated:
        try:
            wage = abs(float(request.POST["bet_money"]))
            percent_to_win = abs(int(request.POST["percent_to_win"]))
        except ValueError:
            return JsonResponse({"status": 1})

        player = CasinoPlayers.objects.get(user=request.user)

        if player.money < wage or not 1 <= percent_to_win <= 90:
            return JsonResponse({"status:": 1})
        else:
            status = 0
            result, message, won_money, lucky_number = casino_actions.make_bet(player, percent_to_win, wage)
            bet = BetsHistory.objects.create(player=player, user_number=percent_to_win, drown_number=lucky_number,
                                             amount=wage, win=result, money=won_money)

            return JsonResponse({"status": status, "message": message, "player_money": format_money(player.money),
                                 "date": "Now", "amount": "%.5f" % wage, "user_number": percent_to_win,
                                 "drown_number": lucky_number, "win": result, "money": bet.money})
    else:
        return JsonResponse({"status": "forbidden"})


@csrf_exempt
@check_post_password
def make_bet_fb(request):
    wage = abs(float(request.POST["bet_money"]))
    percent_to_win = abs(int(request.POST["percent_to_win"]))
    try:
        player = CasinoPlayers.objects.get(user_fb_id=request.POST["fb_user_id"])
    except ObjectDoesNotExist:
        message = FB_REGISTER_ACCOUNT_MESSAGE
    else:
        if player.money < wage:
            message = "🚫 Nie masz wystarczająco pieniędzy"
        elif not 1 <= percent_to_win <= 90:
            message = "🚫 Możesz mieć od 1% do 90% na wygraną"
        else:
            result, message, won_money, lucky_number = casino_actions.make_bet(player, percent_to_win, wage)
            BetsHistory.objects.create(player=player, user_number=percent_to_win, drown_number=lucky_number,
                                       amount=wage, win=result, money=won_money)

    return JsonResponse({"message": message})


@transaction.atomic
def jackpot_buy(request):
    if request.method == "POST" and request.user.is_authenticated:
        player = CasinoPlayers.objects.get(user=request.user)
        tickets_to_buy = abs(int(request.POST["tickets"]))
        status = casino_actions.buy_ticket(player, tickets_to_buy)
        return JsonResponse({"status": status, "tickets": tickets_to_buy, "player_money": format_money(player.money)})
    else:
        return JsonResponse({"status": "forbidden"})


@csrf_exempt
@check_post_password
def jackpot_buy_fb(request):
    try:
        player = CasinoPlayers.objects.get(user_fb_id=request.POST["user_fb_id"])
    except ObjectDoesNotExist:
        message = FB_REGISTER_ACCOUNT_MESSAGE
    else:
        tickets_to_buy = abs(int(request.POST["tickets"]))
        status = casino_actions.buy_ticket(player, tickets_to_buy)
        if status == 0:
            message = f"✅ Kupiono {tickets_to_buy} biletów za {tickets_to_buy} dogecoinów. Użyj komendy !jacpkot żeby dostać więcej informacji"
        elif status == 1:
            message = f"🚫 Nie masz wystarczająco dogecoinów (chciałeś kupić {tickets_to_buy} biletów, a masz {format_money(player.money)} dogecoinów)"
        else:
            message = "💤 Obecnie trwa losowanie, spróbuj za kilka sekund"
    return JsonResponse({"message": message})


def buy_scratch_card(request):
    if request.method == "POST":
        player = CasinoPlayers.objects.get(user=request.user)
        message = casino_actions.buy_scratch_card(player)
        return JsonResponse({"message": message, "player_money": format_money(player.money)})
    else:
        return JsonResponse({"status": "forbidden"})


@csrf_exempt
@check_post_password
def buy_scratch_card_fb(request):
    if request.method == "POST":
        try:
            player = CasinoPlayers.objects.get(user_fb_id=request.POST["user_fb_id"])
        except ObjectDoesNotExist:
            message = FB_REGISTER_ACCOUNT_MESSAGE
        else:
            message = casino_actions.buy_scratch_card(player)
        return JsonResponse({"message": message})
    else:
        return JsonResponse({"status": "forbidden"})


@csrf_exempt
@check_post_password
def create_account_fb(request):
    try:
        CasinoPlayers.objects.create(user_fb_id=request.POST["user_fb_id"], fb_name=request.POST["fb_name"])
        message = "✅ Pomyślnie się zarejestrowano. Jest możliwa integracja ze stroną www (https://dogson.ovh). Po więcej informacji napisz !strona"
    except IntegrityError:
        message = "🚫 Masz już założone konto"
    return JsonResponse({"message": message})


def shop(request):
    if request.method == "POST":
        player = CasinoPlayers.objects.get(user=request.user)
        item_id = request.POST["item_id"]
        message = casino_actions.shop(player, item_id)
        return JsonResponse({"message": message})
    else:
        return JsonResponse({"status": "forbidden"})


@csrf_exempt
@check_post_password
def shop_fb(request):
    if request.method == "POST":
        try:
            player = CasinoPlayers.objects.get(user_fb_id=request.POST["user_fb_id"])
        except ObjectDoesNotExist:
            message = FB_REGISTER_ACCOUNT_MESSAGE
        else:
            item_id = request.POST["item_id"]
            message = casino_actions.shop(player, item_id)
        return JsonResponse({"message": message})
    else:
        return JsonResponse({"status": "forbidden"})
