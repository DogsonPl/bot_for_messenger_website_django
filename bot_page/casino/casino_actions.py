from decimal import Decimal, getcontext
import os
import bisect
import struct
from datetime import datetime, timedelta
import pytz
import json
from asgiref.sync import async_to_sync
import random as rd
from collections import Counter
from dataclasses import dataclass
from typing import Tuple, Union

from django.db import transaction, ProgrammingError
from django.db.models import ObjectDoesNotExist
from django.core.cache import cache
from django.conf import settings
import channels.layers

from utils import statistic_data
from .models import Jackpot, CasinoPlayers, AchievementsPlayerLinkTable, Achievements, Shop
from .utils import format_money, count_scratch_card_timeout
from .achievements import AchievementsCheck, ACHIEVEMENTS
from . import shop

shop_obj = shop.Shop()
getcontext().prec = 20
achievement_check = AchievementsCheck()
Achievements.create_achievements(ACHIEVEMENTS)
Shop.create_shop_table(shop_obj.SHOP_ITEMS)

try:
    WIN_DOGECOINS_ACHIEVEMENT = Achievements.objects.get(id=Achievements.win_dogecoins_in_one_bet_achievement_id)
    WIN_DOGECOINS_IN_A_ROW_ACHIEVEMENT = Achievements.objects.get(id=Achievements.win_dogecoins_in_a_row_id)
    DONE_BETS_ACHIEVEMENT = Achievements.objects.get(id=Achievements.done_bets_achievement_id)
    BOUGHT_SCRATCHES_IN_ONE_DAY = Achievements.objects.get(id=Achievements.bought_scratches_in_one_day_id)
    WIN_2500_SCRATCH_ACHIEVEMENT = Achievements.objects.get(id=Achievements.win_2500_scratch_achievement_id)
    BOUGHT_SCRATCHES = Achievements.objects.get(id=Achievements.bought_scratches_id)
    DAILY_STRIKE_ACHIEVEMENT = Achievements.objects.get(id=Achievements.daily_strike_achievement_id)
    DAILY_STRIKE_TOTAL = Achievements.objects.get(id=Achievements.daily_total_id)
    SLOTKARZ_ID = Achievements.objects.get(id=Achievements.slotakrz_id)
except (ObjectDoesNotExist, ProgrammingError):
    print("Cannot find all achievements on casino/casino_actions.py")


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
SLOTS_PRIZE = {
    "1": 0,
    "2": 3,
    "3": 7,
    "4": 20,
    "5": 100
}


def set_daily(player: CasinoPlayers) -> str:
    if cache.get("performing_daily_reset"):
        return """💤 Obecnie jest wykonywany reset, spróbuj ponownie za kilka sekund"""
    if not player.take_daily:
        players_who_took_daily = CasinoPlayers.objects.filter(take_daily=True)
        number_of_players_who_took_daily = len(players_who_took_daily)
        if number_of_players_who_took_daily == 0:
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
Jest to twoje {player.daily_strike} daily z rzędu i jesteś {number_of_players_who_took_daily+1} osobą która odebrała daily (osoba która jako pierwsza odbierze daily otrzymuje bonusowe 100 dogów)"""

        link_table = AchievementsPlayerLinkTable.objects.get(player=player, achievement=DAILY_STRIKE_ACHIEVEMENT)
        achievement_check.check_achievement_add(DAILY_STRIKE_ACHIEVEMENT, link_table)
        link_table = AchievementsPlayerLinkTable.objects.get(player=player, achievement=DAILY_STRIKE_TOTAL)
        achievement_check.check_achievement_add(DAILY_STRIKE_TOTAL, link_table)

    else:
        message = f"""Odebrano już dzisiaj daily, nie próbuj oszukać systemu 😉. 
Twój daily strike to {player.daily_strike}"""
    return message



@dataclass
class BetData:
    result: int
    message: str
    won_money: Decimal
    lucky_number: float

def make_bet(player: CasinoPlayers, percent_to_win: int, wage: float) -> BetData:
    """
    result 0 --> player lost
    result 1 --> player won
    """
    message = ""
    lucky_number = get_random_number()
    if player.lower_lucky_number_time > datetime.now(tz=pytz.timezone(settings.TIME_ZONE)):
        lucky_number -= 1
        lucky_number = round(lucky_number, 2)
        message += "Będziesz miał/a zmniejszoną losowaną liczbe o 1 jeszcze przez " + str(player.lower_lucky_number_time - datetime.now(tz=pytz.timezone(settings.TIME_ZONE)))[2:7] + "\n\n"
    if lucky_number >= percent_to_win:
        player.lost_bets += 1
        result = 0
        won_money = Decimal(wage*-1)
        player.money += won_money
        player.lost_dc += won_money
        message += f"<strong>📉 𝗣𝗿𝘇𝗲𝗴𝗿𝗮𝗻𝗼 {'%.2f' % wage} dogecoinów</strong>."

        link_table = AchievementsPlayerLinkTable.objects.get(achievement=WIN_DOGECOINS_IN_A_ROW_ACHIEVEMENT, player=player)
        if wage != 0:
            achievement_check.check_achievement_set(WIN_DOGECOINS_IN_A_ROW_ACHIEVEMENT, link_table, 0)

    else:
        player.won_bets += 1
        result = 1
        won_money = Decimal(((wage / (percent_to_win / 100)) - wage) * 0.99)
        if player.bigger_win_time > datetime.now(tz=pytz.timezone(settings.TIME_ZONE)):
            won_money *= Decimal(1.01)
            message += "Twoje wygrane będą powiększane o 1% jeszcze przez " + str(player.bigger_win_time - datetime.now(tz=pytz.timezone(settings.TIME_ZONE)))[2:7] + "\n\n"
        player.money += won_money
        player.won_dc += won_money
        message += f"<strong>📈 𝗪𝘆𝗴𝗿𝗮𝗻𝗼 {'%.2f' % won_money} dogecoinów</strong>."
        if player.biggest_win < won_money:
            player.biggest_win = won_money
            link_table = AchievementsPlayerLinkTable.objects.get(achievement=WIN_DOGECOINS_ACHIEVEMENT, player=player)
            achievement_check.check_achievement_set(WIN_DOGECOINS_ACHIEVEMENT, link_table, won_money)

        link_table = AchievementsPlayerLinkTable.objects.get(achievement=WIN_DOGECOINS_IN_A_ROW_ACHIEVEMENT, player=player)
        if wage == 0:
            achievement_check.check_achievement_set(WIN_DOGECOINS_IN_A_ROW_ACHIEVEMENT, link_table, 0)
        else:
            achievement_check.check_achievement_add(WIN_DOGECOINS_IN_A_ROW_ACHIEVEMENT, link_table)
        if cache.get("max_bet_win") < won_money:
            update_the_biggest_win(player, won_money, percent_to_win, wage)

    message += f"\n𝐌𝐚𝐬𝐳 𝐢𝐜𝐡 𝐨𝐛𝐞𝐜𝐧𝐢𝐞 {format_money(player.money)}\n𝐖𝐲𝐥𝐨𝐬𝐨𝐰𝐚𝐧𝐚 𝐥𝐢𝐜𝐳𝐛𝐚: {lucky_number}"
    link_table = AchievementsPlayerLinkTable.objects.get(player=player, achievement=DONE_BETS_ACHIEVEMENT)
    achievement_check.check_achievement_add(DONE_BETS_ACHIEVEMENT, link_table)
    player.save()

    send_bet_signal(str(player), wage, percent_to_win, lucky_number, result, float(won_money))
    return BetData(result, message, won_money, lucky_number)


def update_the_biggest_win(player: CasinoPlayers, won_money: Decimal, percent_to_win: int, wage: float):
    cache.set("max_bet_win", won_money, None)
    data = cache.get("data")
    data["max_bet_win"]["prize"] = float(won_money)
    data["max_bet_win"]["winner"] = str(player)
    data["max_bet_win"]["percent_to_win"] = percent_to_win
    data["max_bet_win"]["wage"] = int(wage)
    cache.set("data", data, None)
    statistic_data.save()


@transaction.atomic
def buy_ticket(player: CasinoPlayers, tickets_to_buy: int) -> int:
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


def buy_scratch_card(player: CasinoPlayers):
    if player.money < 5:
        return "🚫 Nie masz wystarczająco dogecoinów by kupić zdrapke, koszt zdrapki to 5 dogecoinów"
    message = ""
    if player.faster_scratch_time > datetime.now(tz=pytz.timezone(settings.TIME_ZONE)):
        message += "Będziesz mógł odbierać szybciej zdrapki jeszcze przez " + str(player.faster_scratch_time - datetime.now(tz=pytz.timezone(settings.TIME_ZONE)))[0:8] + "\n\n"
        minutes = 10
    else:
        minutes = 20
    try:
        if player.last_time_scratch > datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) - timedelta(minutes=minutes):
            timeout = count_scratch_card_timeout(player, minutes)
            message += f"""⏳ Możesz kupić jedną zdrapke w ciągu 20 minut
Kolejną możesz odebrać za {timeout} minut"""
            return message
    except TypeError:
        pass
    scratch_prize = get_scratch_prize()
    profit = scratch_prize-5
    player.money += profit
    player.last_time_scratch = datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
    player.today_scratch_bought += 1
    player.total_scratch_bought += 1

    link_table = AchievementsPlayerLinkTable.objects.get(player=player, achievement=BOUGHT_SCRATCHES_IN_ONE_DAY)
    achievement_check.check_achievement_add(BOUGHT_SCRATCHES_IN_ONE_DAY, link_table)
    link_table = AchievementsPlayerLinkTable.objects.get(player=player, achievement=BOUGHT_SCRATCHES)
    achievement_check.check_achievement_add(BOUGHT_SCRATCHES, link_table)
    if scratch_prize == 2500:
        link_table = AchievementsPlayerLinkTable.objects.get(player=player, achievement=WIN_2500_SCRATCH_ACHIEVEMENT)
        achievement_check.check_achievement_add(WIN_2500_SCRATCH_ACHIEVEMENT, link_table)
    player.save()

    message += f"""🔢 𝗪 𝘇𝗱𝗿𝗮𝗽𝗰𝗲 𝘄𝘆𝗴𝗿𝗮𝗹𝗲𝘀/𝗮𝘀 {scratch_prize} dogów, profit to {profit} dogów
𝐌𝐚𝐬𝐳 𝐢𝐜𝐡 𝐨𝐛𝐞𝐜𝐧𝐢𝐞 {format_money(player.money)} dogów"""
    return message


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


def send_bet_signal(player_name: str, wage: float, lucky_number: int, drawn_number: float, result: int, won_money: Decimal):
    bet_info = [player_name, "%.5f" % wage, lucky_number, drawn_number, result, "%.3f" % won_money]
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "players", {
            "type": 'new_bet',
            "content": json.dumps({"bet_info": bet_info, "win": result})
        })


def shop(player: CasinoPlayers, item_id: int):
    try:
        shop_item = shop_obj.SHOP_ITEMS[int(item_id)-1]
        if shop_item["cost"] < player.legendary_dogecoins:
            message = shop_item["function"](player)
            player.save()
            bought = True
        else:
            message = f"🚫 Nie masz wystarczająco legendarnych dogecoinów (żeby kupić tego boosta trzeba mieć {shop_item['cost']} legendarnych dogecoinów, ty posiadasz {format_money(player.legendary_dogecoins)})"
            bought = False
    except (IndexError, ValueError):
        message = "🚫 Nie ma boosta o takiej nazwie"
        bought = False
    return message, bought


def slots_game(player: CasinoPlayers) -> Tuple[str, list, Union[int, None]]:
    if player.money < 5:
        return f"🚫 Zagranie kostuje 5 dogów, a masz {format_money(player.money)} dogów", [], None

    player.money -= 5
    nums = []
    for _ in range(5):
        nums.append(rd.randint(1, 5))
    most_common_num, quantity = Counter(nums).most_common()[0]
    prize = SLOTS_PRIZE[str(quantity)]

    link_table = AchievementsPlayerLinkTable.objects.get(player=player, achievement=SLOTKARZ_ID)
    achievement_check.check_achievement_add(SLOTKARZ_ID, link_table)
    player.money += prize
    player.save()

    return f"{quantity} razy został wylosowany numer {most_common_num}, daje ci to {prize} dogów\n𝐌𝐚𝐬𝐳 𝐢𝐜𝐡 𝐨𝐛𝐞𝐜𝐧𝐢𝐞 {format_money(player.money)}", nums, most_common_num
