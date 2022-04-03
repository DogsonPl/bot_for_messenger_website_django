"""
Achievements:
create account [1] id: 1
won jackpots [1, 3, 5] id: 2
done bets [500, 5000, 50000] id: 3
won dogecoins in one bet [100, 1000, 10000] id: 4
won dogecoins in a row in bets [5, 10, 15] (reset when player wages 0 dogecoins and win) id: 5
bought scratches in one day [5, 15, 30] id: 6
won 2500 in the scratch [1, 3, 5] id: 7
bought scratches [50, 200, 750] id: 8
get daily strike [20, 100, 365] id: 9
take daily x times [50, 200, 500] id: 10
play in slots x ttimes [150, 400, 1000] id: 11
"""

from django.db import IntegrityError
# this import is only for typing hints, must be in try block because this import cause circular import error
try:
    from .models import Achievements, AchievementsPlayerLinkTable
except ImportError:
    Achievements = None
    AchievementsPlayerLinkTable = None

ACHIEVEMENTS = [
    {
        "id": 1,
        "name": "Eluwa",
        "required_score_1": 1,
        "required_score_2": None,
        "required_score_3": None,
        "description": "Załóż konto na stronie https://dogson.ovh. Jak używasz bota na meesengerze użyj komendy !email i !strona"
    },
    {
        "id": 2,
        "name": "Krul kasyna",
        "required_score_1": 1,
        "required_score_2": 3,
        "required_score_3": 5,
        "description": "Wygraj w jackpocie 1, 3, 5 razy"
    },
    {
        "id": 3,
        "name": "Beciarz",
        "required_score_1": 500,
        "required_score_2": 5000,
        "required_score_3": 50000,
        "description": "Wykonaj 500, 5000, 50000 betów"
    },
    {
        "id": 4,
        "name": "Pierdolnięcie",
        "required_score_1": 100,
        "required_score_2": 1000,
        "required_score_3": 10000,
        "description": "Wygraj 100, 1000, 10000 dogów w jednym becie"  # todo zrob tak, gdy nie ma sie tu zadnego levelu osiagniecia i sie wygra ponad 10000 dawalo od razu ostatni level osiagniecia
    },
    {
        "id": 5,
        "name": "Wykrywacz",
        "required_score_1": 5,
        "required_score_2": 10,
        "required_score_3": 15,
        "description": "Nie przegraj dogów podczas 15 betów z rzędu, gdy zebutujesz 0 dogami i wygrasz licznik wygranych z rzedu sie zeruje"
    },
    {
        "id": 6,
        "name": "Użaleznieniec",
        "required_score_1": 5,
        "required_score_2": 15,
        "required_score_3": 30,
        "description": "Odbierz 5, 15, 30 zdrapek jednego dnia"
    },
    {
        "id": 7,
        "name": "Farciarz jebany",
        "required_score_1": 1,
        "required_score_2": 3,
        "required_score_3": 5,
        "description": "Wygraj 2500 dogów w zdrapce 1, 3, 5 razy"
    },
    {
        "id": 8,
        "name": "Zdrapkarz",
        "required_score_1": 50,
        "required_score_2": 200,
        "required_score_3": 750,
        "description": "Kup razem 50, 200, 750 zdrapek"
    },
    {
        "id": 9,
        "name": "Kasynoholik",
        "required_score_1": 20,
        "required_score_2": 100,
        "required_score_3": 365,
        "description": "Odbieraj daily 20, 100, 365 dni z rzędu"
    },
    {
        "id": 10,
        "name": "Weteran",
        "required_score_1": 50,
        "required_score_2": 200,
        "required_score_3": 500,
        "description": "Odbierz daily łącznie 50, 200, 500 razy"
    },
    {
        "id": 11,
        "name": "Slotkarz",
        "required_score_1": 150,
        "required_score_2": 400,
        "required_score_3": 1000,
        "description": "Zagraj w gre slots łącznie 15, 400, 1000 razy"
    }
]


class AchievementsCheck:
    create_account_achievement_id = 1
    win_jackpot_achievement_id = 2
    done_bets_achievement_id = 3
    win_dogecoins_in_one_bet_achievement_id = 4
    win_dogecoins_in_a_row_id = 5
    bought_scratches_in_one_day_id = 6
    win_2500_scratch_achievement_id = 7
    bought_scratches_id = 8
    daily_strike_achievement_id = 9
    daily_total_id = 10
    slotakrz_id = 11

    def check_achievement_add(self, achievement: Achievements, achievement_link: AchievementsPlayerLinkTable, player_score_add=1):
        achievement_link.player_score += player_score_add
        self._check_achievement(achievement, achievement_link)

    def check_achievement_set(self, achievement: Achievements, achievement_link: AchievementsPlayerLinkTable, player_score_set):
        achievement_link.player_score = player_score_set
        self._check_achievement(achievement, achievement_link)

    @staticmethod
    def _check_achievement(achievement: Achievements, achievement_link: AchievementsPlayerLinkTable):
        if achievement.required_score_1 <= achievement_link.player_score:
            achievement_link.achievement_level = 1
        try:
            if achievement_link.achievement_level == 1:
                if achievement.required_score_2 <= achievement_link.player_score:
                    achievement_link.achievement_level = 2
            if achievement_link.achievement_level == 2:
                if achievement.required_score_3 <= achievement_link.player_score:
                    achievement_link.achievement_level = 3
        except TypeError:
            # there are not 3 levels of achievements and achievement.required_score is None
            pass
        achievement_link.save()

# todo dodaj osiagniecie wygraj [50, 100, 1000] dueli - id: 10
