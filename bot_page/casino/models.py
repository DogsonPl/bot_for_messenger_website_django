from django.db import models
from django.db.utils import IntegrityError
from django.conf import settings

from .achievements import AchievementsCheck


class CasinoPlayers(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
                                related_name="user")
    user_fb_id = models.CharField(unique=True, max_length=20, blank=True, null=True)
    user_discord_id = models.CharField(unique=True, max_length=20, blank=True, null=True)
    fb_name = models.CharField(max_length=75, blank=True, null=True)
    discord_name = models.CharField(max_length=75, blank=True, null=True)
    money = models.DecimalField(default=0, decimal_places=10, max_digits=20)
    email = models.EmailField(unique=True, blank=True, null=True, max_length=100)
    take_daily = models.BooleanField(default=0)
    daily_strike = models.PositiveSmallIntegerField(default=0)
    won_bets = models.PositiveBigIntegerField(default=0)
    lost_bets = models.PositiveBigIntegerField(default=0)
    last_time_scratch = models.DateTimeField(blank=True, null=True)
    total_scratch_bought = models.PositiveSmallIntegerField(default=0)
    today_scratch_bought = models.PositiveSmallIntegerField(default=0)
    legendary_dogecoins = models.FloatField(default=0)
    biggest_win = models.DecimalField(default=0, decimal_places=10, max_digits=20)
    last_season_dogecoins = models.DecimalField(default=0, decimal_places=10, max_digits=20)
    best_season = models.DecimalField(default=0, decimal_places=10, max_digits=20)
    season_first_place = models.PositiveSmallIntegerField(default=0)
    season_second_place = models.PositiveSmallIntegerField(default=0)
    season_third_place = models.PositiveSmallIntegerField(default=0)
    won_dc = models.DecimalField(default=0, decimal_places=10, max_digits=30)
    lost_dc = models.DecimalField(default=0, decimal_places=10, max_digits=30)

    class Meta:
        verbose_name = "Player"
        verbose_name_plural = "Players"
        db_table = "casino_players"

    def __str__(self):
        if self.user:
            return str(self.user)
        elif self.fb_name:
            return self.fb_name
        else:
            return "Deleted"


class Jackpot(models.Model):
    tickets = models.PositiveIntegerField(default=0)
    player = models.OneToOneField(CasinoPlayers, models.CASCADE, related_name="player_jackpot")

    class Meta:
        verbose_name = "Jackpot"
        verbose_name_plural = "Jackpot"
        db_table = "jackpot"

    def __str__(self):
        return str(self.player)


class JackpotsResults(models.Model):
    winner = models.ForeignKey(CasinoPlayers, null=True, on_delete=models.SET_NULL,
                               related_name="player_jackpots_results")
    prize = models.PositiveIntegerField()
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Jackpot result"
        verbose_name_plural = "Jackpots Results"
        db_table = "jackpots_results"

    def __str__(self):
        return f"Jackpot from {self.date}"


class BetsHistory(models.Model):
    player = models.ForeignKey(CasinoPlayers, null=True, on_delete=models.SET_NULL, related_name="player_bets_history")
    user_number = models.PositiveSmallIntegerField(null=False, blank=False)
    drown_number = models.FloatField(null=False, blank=False)
    amount = models.FloatField(null=False, blank=False)
    # 0 - user lost, 1 - user won
    win = models.BooleanField(null=False, blank=False)
    money = models.FloatField(null=False, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bet"
        verbose_name_plural = "Bets history"
        db_table = "bets_history"

    def __str__(self):
        return f"Bet nr {self.pk} - {self.player}"


class MoneyHistory(models.Model):
    player = models.ForeignKey(CasinoPlayers, models.CASCADE, related_name="player_money_history")
    money = models.FloatField()
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Money history data"
        verbose_name_plural = "Money history"
        db_table = 'money_history'

    def __str__(self):
        return f"Pięniądze użytkownika {self.player} z {self.date}"


class TwentyFourHoursMoneyHistory(models.Model):
    player = models.ForeignKey(CasinoPlayers, models.CASCADE, related_name="player_twenty_four_hours_history_data")
    money = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Money daily history data"
        verbose_name_plural = "Money daily history"
        db_table = "twenty_four_hours_money_history"

    def __str__(self):
        return f"Pięniądze użytkownika {self.player} z {self.date}"


class UsersTotalMoneyHistory(models.Model):
    total_money = models.FloatField(null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Total money history data"
        verbose_name_plural = "Total money history data"
        db_table = "users_total_money_history"

    def __str__(self):
        return f"Dane z {self.date}"


class Achievements(models.Model, AchievementsCheck):
    required_score_1 = models.FloatField(default=1, null=False, blank=False)
    required_score_2 = models.FloatField(default=None, null=True, blank=False)
    required_score_3 = models.FloatField(default=None, null=True, blank=False)
    name = models.CharField(max_length=75, null=False, blank=False, unique=True)
    description = models.CharField(default="Soon", max_length=500, null=False)

    class Meta:
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"
        db_table = "achievements"

    @staticmethod
    def create_achievements(achievements):
        try:
            for i in achievements:
                achievement, created = Achievements.objects.update_or_create(id=i["id"])
                achievement.name = i["name"]
                achievement.description = i["description"]
                achievement.required_score_1 = i["required_score_1"]
                achievement.required_score_2 = i["required_score_2"]
                achievement.required_score_3 = i["required_score_3"]
                achievement.save()
        except IntegrityError:
            print("Probably migrations are running, achievements haven't been updated")

    def __str__(self):
        return self.name


class AchievementsPlayerLinkTable(models.Model):
    player = models.ForeignKey(CasinoPlayers, models.CASCADE, related_name="player_achievements",
                               null=False, blank=False)
    achievement = models.ForeignKey(Achievements, models.CASCADE, related_name="achievements",
                                    null=False, blank=False)
    player_score = models.FloatField(default=0, null=False, blank=False)
    achievement_level = models.SmallIntegerField(default=0, null=False, blank=False)

    class Meta:
        verbose_name = "achievement_link"
        verbose_name_plural = "achievements_links"
        db_table = "achievements_players_link_table"

    def __str__(self):
        return f"{self.player} - {self.achievement}"
