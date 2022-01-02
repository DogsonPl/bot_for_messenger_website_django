from django.db.models.signals import post_save
from django.db import ProgrammingError
from django.db.models import ObjectDoesNotExist
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth import get_user_model

from .models import JackpotsResults, BetsHistory, CasinoPlayers, Achievements, AchievementsPlayerLinkTable
from utils import statistic_data

User = get_user_model()

# achievements
try:
    CREATE_ACCOUNT_ACHIEVEMENT = Achievements.objects.get(id=Achievements.create_account_achievement_id)
except (ObjectDoesNotExist, ProgrammingError):
    print(f"Cannot find all achievements on casino/signals.py")


@receiver(post_save, sender=JackpotsResults, dispatch_uid="check_jackpot_uid")
def check_if_this_is_the_biggest_jackpot_win(sender, instance, created, **kwargs):
    if instance.prize > cache.get("max_jackpot_win"):
        cache.set("max_jackpot_win", instance.prize, None)
        data = cache.get("data")
        data["max_jackpot_win"] = {"prize": int(instance.prize), "winner":  str(instance.winner)}
        cache.set("data", data, None)
        statistic_data.save()


@receiver(post_save, sender=BetsHistory, dispatch_uid="on_bet_uid")
def on_bet(sender, instance, created, **kwargs):
    user_bets = BetsHistory.objects.filter(player=instance.player)
    if len(user_bets) > 10:
        user_bets[0].delete()


@receiver(post_save, sender=CasinoPlayers, dispatch_uid="on_player_created_uid")
def on_casino_player_created(sender, instance, created, **kwargs):
    if created:
        for i in Achievements.objects.all():
            AchievementsPlayerLinkTable.objects.create(player=instance, achievement=i)


@receiver(post_save, sender=Achievements, dispatch_uid="on_new_achievement_uid")
def on_new_achievement(sender, instance, created, **kwargs):
    if created:
        for i in CasinoPlayers.objects.all():
            AchievementsPlayerLinkTable.objects.create(player=i, achievement=instance)


@receiver(post_save, sender=User, dispatch_uid="on_new_user_created")
def on_new_user_created(sender, instance, created, **kwargs):
    if instance.is_active:
        # give achievement for creating account
        player = CasinoPlayers.objects.get(user=instance)
        link_table = AchievementsPlayerLinkTable.objects.get(achievement=CREATE_ACCOUNT_ACHIEVEMENT, player=player)
        link_table.player_score = 1
        link_table.achievement_level = 1
        link_table.save()
