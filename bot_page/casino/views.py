from django.db import transaction
from django.db.models import Sum, ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import CasinoPlayers, BetsHistory, Jackpot
from .forms import BetForm, JackpotForm
from .utils import check_ip
from . import casino_actions


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
        return render(request, "casino/index.html", {"nav_bar": "casino",
                                                     "bet_form": bet_form,
                                                     "jackpot_form": jackpot_form,
                                                     "player": player,
                                                     "user_bets": user_bets,
                                                     "last_bets": last_bets,
                                                     "total_tickets": total_tickets,
                                                     "user_tickets": user_tickets})
    else:
        # todo demo page
        return redirect("account:login")


def set_daily(request):
    if request.method == "POST" and request.user.is_authenticated:
        player = CasinoPlayers.objects.get(user=request.user)
        message = casino_actions.set_daily(player)
        return JsonResponse({"player_money": player.money, "daily_strike": player.daily_strike, "received": message})
    else:
        return JsonResponse({"status": "forbidden"})


@csrf_exempt
@check_ip
def set_daily_fb(request):
    if request.method == "POST":
        player = CasinoPlayers.objects.get(user_fb_id=request.POST["fb_user_id"])
        message = casino_actions.set_daily(player)
        return JsonResponse({"message": message})
    else:
        return JsonResponse({"status": "forbidden"})


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

            return JsonResponse({"status": status, "message": message, "player_money": player.money,
                                 "date": "Now", "amount": wage, "user_number": percent_to_win,
                                 "drown_number": lucky_number, "win": result, "money": bet.money})
    else:
        return JsonResponse({"status": "forbidden"})


@csrf_exempt
@check_ip
def make_bet_fb(request):
    if request.method == "POST":
        wage = float(request.POST["bet_money"])
        percent_to_win = int(request.POST["percent_to_win"])
        player = CasinoPlayers.objects.get(user_fb_id=request.POST["fb_user_id"])
        if player.money < wage or not 1 <= percent_to_win <= 90:
            message = "🚫 Nie masz wystarczająco pieniędzy"
        else:
            result, message, won_money, lucky_number = casino_actions.make_bet(player, percent_to_win, wage)
            BetsHistory.objects.create(player=player, user_number=percent_to_win, drown_number=lucky_number,
                                       amount=wage, win=result, money=won_money)

        return JsonResponse({"message": message})
    return JsonResponse({"status": "forbidden"})


@transaction.atomic
def jackpot_buy(request):
    if request.method == "POST" and request.user.is_authenticated:
        player = CasinoPlayers.objects.get(user=request.user)
        tickets_to_buy = abs(int(request.POST["tickets"]))
        if player.money > tickets_to_buy:
            status = 0
            player.money -= tickets_to_buy
            jackpot, crated = Jackpot.objects.get_or_create(player=player)
            jackpot.tickets += tickets_to_buy
            jackpot.save()
            player.save()
        else:
            status = 1
        return JsonResponse({"status": status, "tickets": tickets_to_buy, "player_money": player.money})
    else:
        return JsonResponse({"status": "forbidden"})
