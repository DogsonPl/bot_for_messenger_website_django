from django.core.cache import cache
import json


__STATISTIC_FILEPATH = "casino//data//statistic.json"


def init():
    with open(__STATISTIC_FILEPATH, "r") as file:
        data = json.load(file)

    cache.set("data", data, None)
    cache.set("max_jackpot_win", data["max_jackpot_win"]["prize"], None)
    cache.set("max_bet_win",  data["max_bet_win"]["prize"], None)
    print("Saved statistic data to cache")


def save():
    with open(__STATISTIC_FILEPATH, "w") as file:
        json.dump(cache.get("data"), file)
