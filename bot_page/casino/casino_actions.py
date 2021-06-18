from decimal import Decimal, getcontext
import os
import struct
from django.db import transaction
from .models import Jackpot, CasinoPlayers

getcontext().prec = 20


def set_daily(player):
    if not player.take_daily:
        players_who_take_daily = CasinoPlayers.objects.filter(take_daily=True)
        if len(players_who_take_daily) == 0:
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


def make_bet(player, percent_to_win, wage):
    """
    result 0 --> player lost
    result 1 --> player won
    """
    lucky_number = get_random_number()
    if lucky_number >= percent_to_win:
        result = 0
        won_money = Decimal(wage*-1)
        player.money += won_money
        message = f"""<strong>📉 Przegrano {'%.2f' % wage} dogecoinów</strong>.  
Masz ich obecnie {'%.2f' % player.money} 
Wylosowana liczba: {lucky_number}"""
    else:
        result = 1
        won_money = Decimal(((wage / (percent_to_win / 100)) - wage) * 0.99)
        player.money += won_money
        message = f"""<strong>📈 Wygrano {'%.2f' % float(won_money)} dogecoinów</strong>.  
Masz ich obecnie {'%.2f' % player.money} 
Wylosowana liczba: {lucky_number}"""
    player.save()
    return result, message, won_money, lucky_number


@transaction.atomic
def buy_ticket(player, tickets_to_buy):
    """
    the ticket costs 1 dogecoin
    """
    if player.money > tickets_to_buy:
        status = 0
        player.money -= tickets_to_buy
        jackpot, crated = Jackpot.objects.get_or_create(player=player)
        jackpot.tickets += tickets_to_buy
        jackpot.save()
        player.save()
    else:
        status = 1
    return status


def get_random_number() -> int:
    """:return random number from 0 to 99"""
    random_bytes = os.urandom(2)
    random = struct.unpack("H", random_bytes)[0] % 100   # "H" --> unsigned short
    return random
