from django.contrib import admin
# Register your models here.
from .models import CasinoPlayers, Jackpot, JackpotsResults, BetsHistory, MoneyHistory, UsersTotalMoneyHistory, \
                    TwentyFourHoursMoneyHistory


@admin.register(CasinoPlayers)
class CasinoPLayersAdmin(admin.ModelAdmin):
    list_display = ("__str__", "email", "money")
    search_fields = ("email__startswith", "user__username__startswith", "fb_name__startswith", "user_fb_id__startswith")


@admin.register(Jackpot)
class JackpotAdmin(admin.ModelAdmin):
    list_display = ("player", "tickets")
    search_fields = ("player__user__username__startswith",)


@admin.register(JackpotsResults)
class JackpotsResultsAdmin(admin.ModelAdmin):
    list_display = ("__str__", "winner", "prize")
    search_fields = ("player__user__username__startswith",)


@admin.register(BetsHistory)
class BetsHistoryAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user_number", "drown_number", "amount", "win", "money", "date")
    search_fields = ("player__user__username__startswith",)
    list_filter = ("win",)


@admin.register(MoneyHistory)
class MoneyHistoryAdmin(admin.ModelAdmin):
    list_display = ("__str__", "money")
    search_fields = ("player__user__username__startswith", "date")


@admin.register(UsersTotalMoneyHistory)
class UsersTotalMoneyHistoryAdmin(admin.ModelAdmin):
    list_display = ("__str__", "total_money")
    search_fields = ("date",)


@admin.register(TwentyFourHoursMoneyHistory)
class TwentyFourHoursMoneyHistory(admin.ModelAdmin):
    list_display = ("__str__", "money")
    search_fields = ("player__user__username__startswith",)
