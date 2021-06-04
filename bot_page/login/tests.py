from django.test import TestCase, Client
from django.apps import apps
from .models import User
# Create your tests here.
CasinoPlayers = apps.get_model("casino", "CasinoPlayers")


class TestLinks(TestCase):
    def setUp(self):
        self.client = Client()

    def test_login(self):
        response = self.client.get("/account/login")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["nav_bar"], "account")
        self.assertTemplateUsed(response, "login/login.html")

    def test_register_page(self):
        response = self.client.get("/account/register")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["nav_bar"], "account")
        self.assertTemplateUsed(response, "login/register.html")

    def test_logout(self):
        response = self.client.get("/account/logout")
        self.assertEqual(response.status_code, 302)

    def test_invalid_activation_link(self):
        response = self.client.get("/account/activate/bad/bad")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Niepoprawny link aktywacyjny")

    def test_settings_link_logged_user(self):
        user = User.objects.create(email="testt@teffsfs.com", password="1234567890")
        CasinoPlayers.objects.create(user=user)
        self.client.force_login(user)
        response = self.client.get("/account/settings")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/account_settings.html")

    def test_settings_link_not_logged(self):
        response = self.client.get("/account/settings")
        self.assertEqual(response.status_code, 302)


class TestUserModel(TestCase):
    def test_create_normal_user(self):
        user = User.objects.create_user(email="tesgfgs@fsfdfsfsf.com", password="blglvsdvs")
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_create_super_user(self):
        user = User.objects.create_superuser(email="FDSFDSFSffsf$@ffds.com", password="Dadaddsa")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
