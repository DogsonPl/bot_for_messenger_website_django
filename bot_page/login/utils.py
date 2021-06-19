from django.contrib.auth import get_user_model
from django.apps import apps
from django.db.models import ObjectDoesNotExist

User = get_user_model()
CasinoPlayers = apps.get_model("casino", "CasinoPlayers")


def create_casino_player_account(user):
    try:
        player = CasinoPlayers.objects.get(email=user.email)
    except ObjectDoesNotExist:
        player = CasinoPlayers.objects.create(user=user, email=user.email)
    else:
        player.user = user

    if user.referrer:
        player.money += 50
        referrer = User.objects.get(referral_code=user.referrer)
        referrer.referrals += 1
        referrer.save()
        referrer_player = CasinoPlayers.objects.get(user=referrer)
        referrer_player.money += 50
        referrer_player.save()

    player.save()
