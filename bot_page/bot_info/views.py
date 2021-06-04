from django.shortcuts import render
from django.apps import apps
from django.db.models import Sum
from django.core.cache import cache
from .utils import serialize
# Create your views here.

# todo do gulpfile working
CasinoPlayers = apps.get_model("casino", "CasinoPlayers")
MoneyHistory = apps.get_model("casino", "MoneyHistory")
TwentyFourHoursMoneyHistory = apps.get_model("casino", "TwentyFourHoursMoneyHistory")
UsersTotalMoneyHistory = apps.get_model("casino", "UsersTotalMoneyHistory")
JackpotsResults = apps.get_model("casino", "JackpotsResults")


def index(request):
    if request.user.is_authenticated:
        user_player = CasinoPlayers.objects.get(user=request.user)
        user_money_statistic_data = MoneyHistory.objects.filter(player=user_player)
        user_money_statistic_data = serialize(user_money_statistic_data)
        user_money_daily_statistic_data = TwentyFourHoursMoneyHistory.objects.filter(player=user_player)
        user_money_daily_statistic_data = serialize(user_money_daily_statistic_data)
    else:
        user_player = None
        user_money_statistic_data = []
        user_money_daily_statistic_data = []

    players = CasinoPlayers.objects.all().order_by("-money")[:10]

    last_jackpots_wins = JackpotsResults.objects.all()
    last_jackpots_wins = serialize(last_jackpots_wins, 5)
    users_total_money_history = UsersTotalMoneyHistory.objects.all()
    users_total_money_history = serialize(users_total_money_history)

    try:
        coins_sum = int(CasinoPlayers.objects.aggregate(total=Sum("money"))["total"])
    except TypeError:
        coins_sum = 0
    biggest_jackpot_win = cache.get("max_jackpot_win")
    biggest_bet_win = cache.get("max_bet_win")
    biggest_bet_winner = cache.get("data")["max_bet_win"]["winner"]
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
                                                   "biggest_jackpot_win": biggest_jackpot_win})
