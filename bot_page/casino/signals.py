from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import JackpotsResults, BetsHistory
from utils import statistic_data


@receiver(post_save, sender=JackpotsResults)
def check_if_this_is_the_biggest_jackpot_win(sender, instance, created, **kwargs):
    if instance.prize > cache.get("max_jackpot_win"):
        cache.set("max_jackpot_win", instance.prize, None)
        data = cache.get("data")
        data["max_jackpot_win"] = {"prize": int(instance.prize), "winner":  str(instance.winner)}
        cache.set("data", data, None)
        statistic_data.save()


@receiver(post_save, sender=BetsHistory)
def on_bet(sender, instance, created, **kwargs):
    user_bets = BetsHistory.objects.filter(player=instance.player)
    if len(user_bets) > 10:
        user_bets[0].delete()
