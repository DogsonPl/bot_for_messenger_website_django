from django.apps import apps
from django.db.models import ObjectDoesNotExist

CasinoPlayers = apps.get_model("casino", "CasinoPlayers")


def create_casino_player_account(user):
    try:
        player = CasinoPlayers.objects.get(email=user.email)
    except ObjectDoesNotExist:
        CasinoPlayers.objects.create(user=user, email=user.email)
    else:
        player.user = user
        player.save()
