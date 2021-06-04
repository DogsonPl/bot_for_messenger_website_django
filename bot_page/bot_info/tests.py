from django.test import TestCase, Client
from django.apps import apps
from django.contrib.auth import get_user_model
# Create your tests here.

CasinoPlayers = apps.get_model("casino", "CasinoPlayers")
User = get_user_model()


class TestLinks(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_not_logged(self):
        response = self.client.get("/bot/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bot_info/index.html")
        self.assertContains(response, "Zaloguj się")
        self.assertNotContains(response, "wyloguj się")
        self.assertEqual(response.context["nav_bar"], "bot_info")
        self.assertIsNone(response.context["player"])
        self.assertEqual(response.context["user_money_statistic_data"], [])

    def test_index_logged(self):
        user = User.objects.create(email="testtesttest@testtest.com", password="1234ZAQ!", username="tests")
        player = CasinoPlayers.objects.create(user=user)
        self.client.force_login(user)
        response = self.client.get("/bot/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bot_info/index.html")
        self.assertContains(response, "Wyloguj się")
        self.assertNotContains(response, "Zaloguj się")
        self.assertEqual(response.context["nav_bar"], "bot_info")
        self.assertEqual(response.context["player"], player)
        self.assertNotEqual(response.context["user_money_statistic_data"], [])
