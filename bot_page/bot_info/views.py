from django.shortcuts import render
from django.apps import apps
from django.db.models import Sum
from django.core.cache import cache

from .utils import serialize_to_json

# Create your views here.

CasinoPlayers = apps.get_model("casino", "CasinoPlayers")
MoneyHistory = apps.get_model("casino", "MoneyHistory")
TwentyFourHoursMoneyHistory = apps.get_model("casino", "TwentyFourHoursMoneyHistory")
UsersTotalMoneyHistory = apps.get_model("casino", "UsersTotalMoneyHistory")
JackpotsResults = apps.get_model("casino", "JackpotsResults")


class NotLoggedUser:
    today_won_money = 0
    today_lost_money = 0


def index(request):
    if request.user.is_authenticated:
        user_player = CasinoPlayers.objects.get(user=request.user)
        total_bets = user_player.won_bets+user_player.lost_bets
        try:
            won_bets_percent = str((user_player.won_bets / total_bets) * 100)[0:5]
        except ZeroDivisionError:
            won_bets_percent = 0
        user_money_statistic_data = MoneyHistory.objects.filter(player=user_player)
        user_money_statistic_data = serialize_to_json(user_money_statistic_data)
        user_money_daily_statistic_data = TwentyFourHoursMoneyHistory.objects.filter(player=user_player)
        user_money_daily_statistic_data = serialize_to_json(user_money_daily_statistic_data)
    else:
        total_bets = 0
        won_bets_percent = 0
        user_player = NotLoggedUser
        user_money_statistic_data = []
        user_money_daily_statistic_data = []

    players = CasinoPlayers.objects.all().order_by("-money")[:10]
    players_legendary = CasinoPlayers.objects.all().order_by("-legendary_dogecoins")[:10]

    last_jackpots_wins = JackpotsResults.objects.all()
    last_jackpots_wins = serialize_to_json(last_jackpots_wins, 5)
    users_total_money_history = UsersTotalMoneyHistory.objects.all()
    users_total_money_history = serialize_to_json(users_total_money_history, 50)

    try:
        coins_sum = int(CasinoPlayers.objects.aggregate(total=Sum("money"))["total"])
    except TypeError:
        coins_sum = 0
    biggest_jackpot_win = cache.get("max_jackpot_win")
    biggest_bet_win = cache.get("max_bet_win")
    biggest_bet_winner = cache.get("data")["max_bet_win"]["winner"]

    last_jackpot_winner = cache.get("last_jackpot_winner")
    last_jackpot_win_prize = cache.get("last_jackpot_win_prize")
    return render(request, "bot_info/index.html", {"nav_bar": "bot_info",
                                                   "player": user_player,
                                                   "players": players,
                                                   "last_jackpots_wins": last_jackpots_wins,
                                                   "users_total_money_history": users_total_money_history,
                                                   "user_money_statistic_data": user_money_statistic_data,
                                                   "user_money_daily_statistic_data": user_money_daily_statistic_data,
                                                   "coins_sum": coins_sum,
                                                   "biggest_bet_win": biggest_bet_win,
                                                   "biggest_bet_winner": biggest_bet_winner,
                                                   "biggest_jackpot_win": biggest_jackpot_win,
                                                   "last_jackpot_winner": last_jackpot_winner,
                                                   "last_jackpot_win_prize": last_jackpot_win_prize,
                                                   "players_legendary": players_legendary,
                                                   "total_bets": total_bets,
                                                   "won_bets_percent": won_bets_percent})
