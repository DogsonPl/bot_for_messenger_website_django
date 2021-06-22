from datetime import datetime, timedelta
import pytz
import random as rd
import bisect
from django.db import transaction
from django.db.utils import ProgrammingError, OperationalError
from django.db.models import Sum
from django.conf import settings
from django.apps import apps
from django.core.cache import cache


def init():
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from django_apscheduler.jobstores import DjangoJobStore

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


class Models:
    CasinoPlayers = apps.get_model("casino", "CasinoPlayers")
    MoneyHistory = apps.get_model("casino", "MoneyHistory")
    TwentyFourHoursMoneyHistory = apps.get_model("casino", "TwentyFourHoursMoneyHistory")
    UsersTotalMoneyHistory = apps.get_model("casino", "UsersTotalMoneyHistory")
    Jackpot = apps.get_model("casino", "Jackpot")
    JackpotsResults = apps.get_model("casino", "JackpotsResults")


@transaction.atomic
def save_hourly_money_history():
    expired_date = datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) - timedelta(days=1)
    Models.TwentyFourHoursMoneyHistory.objects.filter(date__lt=expired_date).delete()
    users_data = Models.CasinoPlayers.objects.all()
    Models.TwentyFourHoursMoneyHistory.objects.bulk_create(
        [Models.TwentyFourHoursMoneyHistory(player=i, money=i.money) for i in users_data])


def save_daily_money_history():
    users_data = Models.CasinoPlayers.objects.all()
    Models.MoneyHistory.objects.bulk_create([Models.MoneyHistory(player=i, money=i.money) for i in users_data])


def save_money_sum_of_all_players():
    total_money = Models.CasinoPlayers.objects.all().aggregate(total_money=Sum("money"))["total_money"]
    Models.UsersTotalMoneyHistory.objects.create(total_money=total_money)


@transaction.atomic
def draw_jackpot_winner():
    players = Models.Jackpot.objects.all()
    tickets = []
    users = []
    for i in players:
        tickets.append(i.tickets)
        users.append(i.player)
    if not tickets:
        # no one bought tickets to play in jackpot
        pass
    else:
        total = 0
        try:
            weights = [total := total + i for i in tickets]
        except SyntaxError:
            raise SyntaxError("To run this function, you have to update your python version to 3.8+")
        random = rd.random() * total
        winner_index = bisect.bisect(weights, random)
        winner = users[winner_index]
        Models.JackpotsResults.objects.create(winner=winner, prize=total)
        winner.money += total
        winner.save()
        Models.Jackpot.objects.all().delete()
        set_last_jackpot_info()


def reset_daily():
    Models.CasinoPlayers.objects.filter(take_daily=False).update(daily_strike=0)
    Models.CasinoPlayers.objects.all().update(take_daily=False)


def set_last_jackpot_info():
    try:
        last_jackpot = Models.JackpotsResults.objects.all().order_by("-id")
        try:
            last_jackpot = last_jackpot[0]
        except IndexError:
            last_jackpot_winner = None
            last_jackpot_win_prize = 0
        else:
            last_jackpot_winner = last_jackpot.winner
            last_jackpot_win_prize = last_jackpot.prize
        cache.set("last_jackpot_winner", last_jackpot_winner)
        cache.set("last_jackpot_win_prize", last_jackpot_win_prize)
    except OperationalError:
        print("Database is probably during migrations")


set_last_jackpot_info()
