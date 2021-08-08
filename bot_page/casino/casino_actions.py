from decimal import Decimal, getcontext
import os
import bisect
import struct
from datetime import datetime, timedelta
import pytz

from django.db import transaction
from django.core.cache import cache
from django.conf import settings

from utils import statistic_data
from .models import Jackpot, CasinoPlayers
from .utils import format_money, count_scratch_card_timeout

getcontext().prec = 20


# key - prize
# value - chance to win
SCRATCH_PRIZES_DICT = {"0": 19,
                       "1": 18,
                       "2": 17,
                       "5": 15,
                       "7": 12,
                       "15": 9,
                       "20": 7,
                       "50": 2.4,
                       "500": 0.5,
                       "2500": 0.1}
SCRATCH_CHANCES = [i for i in SCRATCH_PRIZES_DICT.values()]
SCRATCH_PRIZES = [int(i) for i, _ in SCRATCH_PRIZES_DICT.items()]
PRIZES_SUM = 0
total = 0
SCRATCH_PRIZES_WEIGHTS = [total := total + i for i in SCRATCH_CHANCES]


def set_daily(player) -> str:
    if cache.get("performing_daily_reset"):
        return """💤 Obecnie jest wykonywany reset, spróbuj ponownie za kilka sekund"""
    if not player.take_daily:
        players_who_took_daily = CasinoPlayers.objects.filter(take_daily=True)
        if len(players_who_took_daily) == 0:
            received_bonus = 100
            extra_message = "❤ JESTEŚ PIERWSZĄ OSOBĄ KTÓRA ODEBRAŁA DAILY! OTRZYMUJESZ BONUSOWE 100 DOGÓW\n"
        else:
            received_bonus = 0
            extra_message = ""

        received = 10 + (player.daily_strike / 10) + received_bonus
        player.money += Decimal(received)
        player.daily_strike += 1
        player.take_daily = True
        player.save()
        message = extra_message + f"""✅ Otrzymano właśnie darmowe {'%.2f' % received} dogecoinów.
Jest to twoje {player.daily_strike} daily z rzędu"""
    else:
        message = f"""Odebrano już dzisiaj daily, nie próbuj oszukać systemu 😉. 
Twój daily strike to {player.daily_strike}"""
    return message


def make_bet(player, percent_to_win: int, wage: float):
    """
    result 0 --> player lost
    result 1 --> player won
    """
    lucky_number = get_random_number()
    if lucky_number >= percent_to_win:
        player.lost_bets += 1
        result = 0
        won_money = Decimal(wage*-1)
        player.money += won_money
        player.today_lost_money += float(won_money)
        message = f"""<strong>📉 Przegrano {'%.2f' % wage} dogecoinów</strong>.  
Masz ich obecnie {format_money(player.money)} 
Wylosowana liczba: {lucky_number}"""
    else:
        player.won_bets += 1
        result = 1
        won_money = Decimal(((wage / (percent_to_win / 100)) - wage) * 0.99)
        player.money += won_money
        player.today_won_money += float(won_money)
        message = f"""<strong>📈 Wygrano {'%.2f' % won_money} dogecoinów</strong>.  
Masz ich obecnie {format_money(player.money)} 
Wylosowana liczba: {lucky_number}"""

        if cache.get("max_bet_win") < won_money:
            update_the_biggest_win(player, won_money, percent_to_win, wage)

    player.save()
    return result, message, won_money, lucky_number


def update_the_biggest_win(player, won_money, percent_to_win, wage):
    cache.set("max_bet_win", won_money, None)
    data = cache.get("data")
    data["max_bet_win"]["prize"] = float(won_money)
    data["max_bet_win"]["winner"] = str(player)
    data["max_bet_win"]["percent_to_win"] = percent_to_win
    data["max_bet_win"]["wage"] = int(wage)
    cache.set("data", data, None)
    statistic_data.save()


@transaction.atomic
def buy_ticket(player, tickets_to_buy: int) -> int:
    """
    the ticket costs 1 dogecoin
    status 0 --> player bought tickets
    status 1 --> player doesn't have enough money to buy tickets
    status 2 --> page is performing jackpot draw
    """
    if cache.get("performing_jackpot_draw"):
        status = 2
    elif player.money > tickets_to_buy:
        status = 0
        player.money -= tickets_to_buy
        jackpot, crated = Jackpot.objects.get_or_create(player=player)
        jackpot.tickets += tickets_to_buy
        jackpot.save()
        player.save()
    else:
        status = 1
    return status


def buy_scratch_card(player):
    if player.money < 5:
        return "🚫 Nie masz wystarczająco dogecoinów by kupić zdrapke, koszt zdrapki to 5 dogecoinów"
    try:
        if player.last_time_scratch > datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) - timedelta(minutes=20):
            timeout = count_scratch_card_timeout(player)
            return f"""⏳ Możesz kupić jedną zdrapke w ciągu 20 minut
Kolejną możesz odebrać za {timeout} minut"""
    except TypeError:
        pass
    scratch_prize = get_scratch_prize()
    profit = scratch_prize-5
    player.money += profit
    player.last_time_scratch = datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
    player.today_scratch_profit += profit
    player.today_scratch_bought += 1
    player.save()

    return f"""🔢 W zdrapce wygrałeś/aś {scratch_prize} dogów, profit to {profit} dogów
Obecnie posiadasz {format_money(player.money)} dogów"""


def get_scratch_prize() -> int:
    random_number = get_random_number()
    prize_index = bisect.bisect(SCRATCH_PRIZES_WEIGHTS, random_number)
    prize = SCRATCH_PRIZES[prize_index]
    return prize


def get_random_number() -> float:
    """:return random number from 0 to 99"""
    random_bytes = os.urandom(2)
    random = struct.unpack("H", random_bytes)[0] % 1000   # "H" --> unsigned short
    random /= 10
    return random
