from datetime import datetime, timedelta

import pytz
from django.contrib.auth import settings


class Shop:
    def __init__(self):
        self.SHOP_ITEMS = [
            {
                "id": 1,
                "description": "Przez 12h zdrapki będziesz mógł odbierać co 10min",
                "cost": 200,
                "function": self.faster_scratch
            },
            {
                "id": 2,
                "description": "Losowana liczba będzie o 1 mniejsza przez 1 minute",
                "cost": 2500,
                "function": self.lower_lucky_number
            },
            {
                "id": 3,
                "description": "Twoje wygrane są zwiekszane o 1% przez 1 minute",
                "cost": 2000,
                "function": self.bigger_win
            }
        ]

    def faster_scratch(self, player):
        player.legendary_dogecoins -= self.SHOP_ITEMS[0]["cost"]
        player.faster_scratch_time = datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) + timedelta(hours=12)
        return "✅ Kupiono boosta, który powoduje że możesz odbierać zdrapki co 10min przez 12h"

    def lower_lucky_number(self, player):
        player.legendary_dogecoins -= self.SHOP_ITEMS[1]["cost"]
        player.lower_lucky_number_time = datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) + timedelta(minutes=1)
        return "✅ Kupiono boosta, który powoduje że twoje wylosowane liczby będą zmniejszane o 1 przez 1min"

    def bigger_win(self, player):
        player.legendary_dogecoins -= self.SHOP_ITEMS[2]["cost"]
        player.bigger_win_time = datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) + timedelta(minutes=1)
        return "✅ Kupiono boosta, któru zwiększa twoje wygrane o 1% przez 1min"
