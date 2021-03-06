from datetime import datetime, timedelta
import pytz
import random as rd
import bisect
from decimal import Decimal, getcontext

from django.db import transaction
from django.db.utils import ProgrammingError, OperationalError
from django.db.models import Sum, F, ObjectDoesNotExist
from django.conf import settings
from django.apps import apps
from django.core.cache import cache
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

getcontext().prec = 20

CasinoPlayers = apps.get_model("casino", "CasinoPlayers")
MoneyHistory = apps.get_model("casino", "MoneyHistory")
TwentyFourHoursMoneyHistory = apps.get_model("casino", "TwentyFourHoursMoneyHistory")
UsersTotalMoneyHistory = apps.get_model("casino", "UsersTotalMoneyHistory")
Jackpot = apps.get_model("casino", "Jackpot")
JackpotsResults = apps.get_model("casino", "JackpotsResults")
Achievements = apps.get_model("casino", "Achievements")
AchievementsPlayerLinkTable = apps.get_model("casino", "AchievementsPlayerLinkTable")

# achievements
try:
    WIN_JACKPOT_ACHIEVEMENT = Achievements.objects.get(id=Achievements.win_jackpot_achievement_id)
    BOUGHT_SCRATCHES_IN_ONE_DAY = Achievements.objects.get(id=Achievements.bought_scratches_in_one_day_id)
    DAILY_STRIKE_ACHIEVEMENT = Achievements.objects.get(id=Achievements.daily_strike_achievement_id)
except (ObjectDoesNotExist, ProgrammingError):
    print("Cannot find all achievements on scheduler.py")


def init():
    from django_apscheduler.jobstores import DjangoJobStore

    # these cache values prevent from deadlock
    cache.set("performing_daily_reset", False, None)
    cache.set("performing_jackpot_draw", False, None)

    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(save_hourly_money_history, trigger=CronTrigger(hour="0-23", minute=30),
                      id="save_hourly_money_history", max_instances=1, replace_existing=True)
    scheduler.add_job(save_money_sum_of_all_players, trigger=CronTrigger(hour="0,12,18"),
                      id="save_money_sum_of_all_players", max_instances=1, replace_existing=True)
    scheduler.add_job(save_daily_money_history, trigger=CronTrigger(hour=0, minute=10),
                      id="save_daily_money_history", max_instances=1, replace_existing=True)
    scheduler.add_job(draw_jackpot_winner, trigger=CronTrigger(hour=0),
                      id="draw_jackpot", max_instances=1, replace_existing=True)
    scheduler.add_job(reset_daily, trigger=CronTrigger(hour=0),
                      id="reset_daily", max_instances=1, replace_existing=True)

    try:
        scheduler.start()
    except ProgrammingError:
        print("Restart app to run scheduled tasks")
    else:
        print("Scheduler started")


@transaction.atomic
def save_hourly_money_history():
    expired_date = datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) - timedelta(days=1)
    TwentyFourHoursMoneyHistory.objects.filter(date__lt=expired_date).delete()
    users_data = CasinoPlayers.objects.all()
    TwentyFourHoursMoneyHistory.objects.bulk_create([TwentyFourHoursMoneyHistory(player=i, money=i.money) for i in users_data])


def save_daily_money_history():
    users_data = CasinoPlayers.objects.all()
    MoneyHistory.objects.bulk_create([MoneyHistory(player=i, money=i.money) for i in users_data])


def save_money_sum_of_all_players():
    total_money = CasinoPlayers.objects.all().aggregate(total_money=Sum("money"))["total_money"]
    UsersTotalMoneyHistory.objects.create(total_money=total_money)


@transaction.atomic
def draw_jackpot_winner():
    cache.set("performing_jackpot_draw", True, None)

    players = Jackpot.objects.all()
    if len(players) == 0:
        # no one bought tickets to play in jackpot
        pass
    else:
        tickets = []
        users = []
        for i in players:
            tickets.append(i.tickets)
            users.append(i.player)

        total = 0
        try:
            weights = [total := total + i for i in tickets]
        except SyntaxError:
            raise SyntaxError("To run this function, you have to update your python version to 3.8+")
        random = rd.random() * total
        winner_index = bisect.bisect(weights, random)
        winner = users[winner_index]
        JackpotsResults.objects.create(winner=winner, prize=total)
        winner.money += total
        winner.save()

        Jackpot.objects.all().delete()
        set_last_jackpot_info()
        link_table = AchievementsPlayerLinkTable.objects.get(achievement=WIN_JACKPOT_ACHIEVEMENT, player=winner)
        Achievements().check_achievement_add(WIN_JACKPOT_ACHIEVEMENT, link_table)
        cache.set("performing_jackpot_draw", False, None)


def reset_daily():
    cache.set("performing_daily_reset", True, None)
    now = datetime.now(tz=pytz.timezone(settings.TIME_ZONE))

    #CasinoPlayers.objects.filter(take_daily=False).update(daily_strike=0)
    #AchievementsPlayerLinkTable.objects.filter(achievement=BOUGHT_SCRATCHES_IN_ONE_DAY).update(player_score=0)
    #for i in AchievementsPlayerLinkTable.objects.filter(achievement=DAILY_STRIKE_ACHIEVEMENT):
    #    if not i.player.take_daily:
    #        i.player_score = 0
    #        i.save()
    if now.day == 1:
        try:
            first_player, second_player, third_player = CasinoPlayers.objects.all().order_by('-money')[:3]
            first_player.season_first_place += 1
            first_player.save()
            second_player.season_second_place += 1
            second_player.save()
            third_player.season_third_place += 1
            third_player.save()
        except ValueError:
            # there are not enough players
            pass
        for i in CasinoPlayers.objects.all():
            i.take_daily = False
            i.today_scratch_bought = 0
            i.last_season_dogecoins = i.money
            if i.money > i.best_season:
                i.best_season = i.money
            if i.money > 100:
                i.legendary_dogecoins += float(i.money - 100)
                i.money = 100
            i.save()
    else:
        CasinoPlayers.objects.all().update(take_daily=False,
                                           today_scratch_bought=0, money=F("money")*Decimal("0.99"))
    cache.set("performing_daily_reset", False, None)


def set_last_jackpot_info():
    try:
        last_jackpot = JackpotsResults.objects.all().order_by("-id")
        try:
            last_jackpot = last_jackpot[0]
        except IndexError:
            last_jackpot_winner = None
            last_jackpot_win_prize = 0
        else:
            last_jackpot_winner = last_jackpot.winner
            last_jackpot_win_prize = last_jackpot.prize
        cache.set("last_jackpot_winner", last_jackpot_winner, None)
        cache.set("last_jackpot_win_prize", last_jackpot_win_prize, None)
    except OperationalError:
        print("Database is probably during migrations")


set_last_jackpot_info()
