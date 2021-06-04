from django.test import TestCase, Client
from django.core.cache import cache
from django.contrib.auth import get_user_model
from decimal import Decimal
import random as rd
from .forms import BetForm, JackpotForm
from .casino_actions import set_daily, make_bet
from .models import CasinoPlayers, JackpotsResults, BetsHistory, Jackpot
from .views import EmptyBet
# Create your tests here.

User = get_user_model()


class TestBetForm(TestCase):
    def test_valid_form(self):
        form = BetForm(data={"percent_to_win": 20, "bet_money": 10})
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = BetForm(data={"percent_to_win": "wrong", "bet_money": "wrong"})
        self.assertFalse(form.is_valid())

    def test_invalid_percent_to_win(self):
        form = BetForm(data={"percent_to_win": "wrong", "bet_money": 10})
        self.assertFalse(form.is_valid())

    def test_invalid_bet_money(self):
        form = BetForm(data={"percent_to_win": 20, "bet_money": "wrong"})
        self.assertFalse(form.is_valid())

    def test_empty_form(self):
        form = BetForm(data={"percent_to_win": "", "bet_money": ""})
        self.assertFalse(form.is_valid())

    def test_too_big_percent_to_win(self):
        form = BetForm(data={"percent_to_win": 200, "bet_money": 10})
        self.assertFalse(form.is_valid())

    def test_too_small_percent_to_win(self):
        form = BetForm(data={"percent_to_win": -10, "bet_money": 1043})
        self.assertFalse(form.is_valid())

    def test_negative_bet_money(self):
        form = BetForm(data={"percent_to_win": 50, "bet_money": -10})
        self.assertFalse(form.is_valid())

    def test_float(self):
        form = BetForm(data={"percent_to_win": 21.37, "bet_money": 23})
        self.assertFalse(form.is_valid())


class TestJackpotForm(TestCase):
    def test_valid_form(self):
        form = JackpotForm(data={"tickets": 10})
        self.assertTrue(form.is_valid())

    def test_negative_tickets_to_buy(self):
        form = JackpotForm(data={"tickets": -12})
        self.assertFalse(form.is_valid())

    def test_float(self):
        form = JackpotForm(data={"tickets": 37.21})
        self.assertFalse(form.is_valid())


class TestDatabase(TestCase):
    def setUp(self):
        self.first_player = CasinoPlayers.objects.create(money=350, take_daily=0, daily_strike=0)


class TestBet(TestDatabase):
    def test_lost_bet(self):
        """
         percent to win is set to 0%, so user can`t win
        """
        old_player_money = self.first_player.money
        wage = 50
        percent_to_win = 0
        result, message, won_money, lucky_number = make_bet(player=self.first_player, percent_to_win=percent_to_win, wage=wage)
        self.assertFalse(result)
        self.assertEqual(old_player_money+won_money, self.first_player.money)
        self.assertEqual(message, f"<strong>📉 Przegrano {wage} dogecoinów</strong>. Masz ich obecnie {'%.2f' % self.first_player.money}\nWylosowana liczba: {lucky_number}")
        self.assertEqual(won_money, wage*-1)

    def test_win_bet(self):
        """
        percent to win is set to 0%, so user can`t lost
        """
        old_player_money = self.first_player.money
        wage = 50
        percent_to_win = 100
        result, message, won_money, lucky_number = make_bet(player=self.first_player, percent_to_win=percent_to_win, wage=wage)
        self.assertTrue(result)
        self.assertEqual(old_player_money+won_money, self.first_player.money)
        self.assertEqual(message, f"<strong>📈 Wygrano {'%.2f' % float(won_money)} dogecoinów</strong>. Masz ich obecnie {'%.2f' % self.first_player.money}\nWylosowana liczba: {lucky_number}")
        self.assertEqual(won_money, Decimal(((wage / (percent_to_win / 100)) - wage) * 0.99))

    def test_random_bets(self):
        for _ in range(25):
            old_player_money = self.first_player.money
            wage = rd.uniform(0, 13)
            percent_to_win = rd.randint(1, 91)
            result, message, won_money, lucky_number = make_bet(player=self.first_player, percent_to_win=percent_to_win, wage=wage)
            self.assertEqual(old_player_money + won_money, self.first_player.money)
            if result == 0:
                self.assertEqual(message, f"<strong>📉 Przegrano {wage} dogecoinów</strong>. Masz ich obecnie {'%.2f' % self.first_player.money}\nWylosowana liczba: {lucky_number}")
                self.assertEqual(won_money, wage * -1)
            elif result == 1:
                self.assertEqual(message, f"<strong>📈 Wygrano {'%.2f' % float(won_money)} dogecoinów</strong>. Masz ich obecnie {'%.2f' % self.first_player.money}\nWylosowana liczba: {lucky_number}")
                self.assertEqual(won_money, Decimal(((wage / (percent_to_win / 100)) - wage) * 0.99))
            else:
                raise AssertionError("Result should be equal 0 or 1")


class TestDaily(TestDatabase):
    def test_valid_data(self):
        old_player_money = self.first_player.money
        old_daily_strike = self.first_player.daily_strike
        message = set_daily(self.first_player)
        self.assertEqual(message, f"Otrzymano daily 🥰 A dokładniej {10 + (old_daily_strike / 10)} dogecoinów 😎🤑")
        self.assertEqual(old_player_money + 10 + Decimal((old_daily_strike / 10)), self.first_player.money)
        self.assertEqual(old_daily_strike+1, self.first_player.daily_strike)

    def test_invalid_data(self):
        old_player_money = self.first_player.money
        old_daily_strike = self.first_player.daily_strike
        self.first_player.take_daily = True
        message = set_daily(self.first_player)
        self.assertEqual(message, "Odebrano już dzisiaj daily, nie próbuj oszukać systemu 😉")
        self.assertEqual(self.first_player.money, old_player_money)
        self.assertEqual(old_daily_strike, self.first_player.daily_strike)


class TestSignals(TestDatabase):
    def test_update_the_biggest_jackpot_win(self):
        prize = 10
        cache.set("max_jackpot_win", 0, None)
        JackpotsResults.objects.create(winner=self.first_player, prize=prize)
        self.assertEqual(cache.get("max_jackpot_win"), prize)

    def test_pass_update_biggest_jackpot_win(self):
        prize = 5433
        the_biggest_jackpot_win = 9000
        cache.set("max_jackpot_win", the_biggest_jackpot_win, None)
        JackpotsResults.objects.create(winner=self.first_player, prize=prize)
        self.assertEqual(cache.get("max_jackpot_win"), the_biggest_jackpot_win)

    def test_update_the_biggest_win(self):
        cache.set("max_bet_win", 0, None)
        money = 65.543
        BetsHistory.objects.create(player=self.first_player, user_number=50, drown_number=0, amount=54.654, win=1, money=money)
        self.assertEqual(cache.get("max_bet_win"), money)

    def test_pass_update_the_biggest_win(self):
        biggest_win = 543.3554
        cache.set("max_bet_win", biggest_win, None)
        BetsHistory.objects.create(player=self.first_player, user_number=53, drown_number=40, amount=54, win=1, money=43.43)
        self.assertEqual(cache.get("max_bet_win"), biggest_win)

    def test_update_the_biggest_win_if_lose(self):
        cache.set("max_bet_win", 0, None)
        amount = 65.543
        BetsHistory.objects.create(player=self.first_player, user_number=22, drown_number=43, amount=amount, win=0, money=amount*-1)
        self.assertEqual(cache.get("max_bet_win"), 0)


class TestViews(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@test2.com", password="Test1234%", username="test2")
        self.player = CasinoPlayers.objects.create(user=self.user)
        self.second_user = User.objects.create(email="test@test3.com", password="Test1234%", username="test3")
        self.player.money = rd.uniform(0, 2000)
        self.client = Client()
        Jackpot.objects.create(tickets=200, player=CasinoPlayers.objects.create(user=self.second_user))

    def tearDown(self):
        self.user.delete()
        self.second_user.delete()

    def test_index_page_login(self):
        self.client.force_login(self.user)
        response = self.client.get("/casino/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "casino/index.html")
        self.assertEqual(response.context["nav_bar"], "casino")
        self.assertEqual(response.context["player"], self.player)
        self.assertEqual(response.context["total_tickets"], 200)
        self.assertEqual(response.context["user_tickets"], 0)
        self.assertEqual(response.context["user_bets"], EmptyBet)

    def test_index_page_not_logged_in(self):
        response = self.client.get("/casino/")
        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url, "/account/login")

    def test_set_daily_link(self):
        response = self.client.get("/casino/set_daily")
        self.assertEqual(response.json(), {"status": "forbidden"})

    def test_make_bet_link(self):
        response = self.client.get("/casino/bet")
        self.assertEqual(response.json(), {"status": "forbidden"})

    def test_jackpot_buy_link(self):
        response = self.client.get("/casino/jackpot_buy")
        self.assertEqual(response.json(), {"status": "forbidden"})
