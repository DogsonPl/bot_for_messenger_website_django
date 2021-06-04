from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.apps import apps
from .forms import ContactForm
# Create your tests here.

CasinoPlayers = apps.get_model("casino", "CasinoPlayers")
User = get_user_model()


class TestLinks(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_not_logged(self):
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/index.html")
        self.assertEqual(response.context["nav_bar"], "home")
        self.assertIsNone(response.context["player"])

    def test_index_logged(self):
        user = User.objects.create(email="testte43sttest@testtest.com", password="1234ZAQ!", username="te43sts")
        player = CasinoPlayers.objects.create(user=user)
        self.client.force_login(user)
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/index.html")
        self.assertEqual(response.context["nav_bar"], "home")
        self.assertEqual(response.context["player"], player)

    def test_contact_form_link(self):
        response = self.client.get("/kontakt")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/contact.html")
        self.assertEqual(response.context["nav_bar"], "contact")

    def test_privacy_policy_link(self):
        response = self.client.get("/privacy_policy")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/privacy_policy.html")
