from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterTests(APITestCase):

    def test_register_creates_user_and_signs_them_in(self):
        response = self.client.post(
            "/api/auth/register/",
            {"username": "nick", "password": "sup3r-secret-pw", "email": "nick@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"]["username"], "nick")
        self.assertIn("access", response.data)
        self.assertIn("refresh_token", response.cookies)
        self.assertTrue(response.cookies["refresh_token"]["httponly"])

        user = User.objects.get(username="nick")
        self.assertTrue(user.check_password("sup3r-secret-pw"))

    # the password must never come back out, hashed or otherwise
    def test_register_does_not_echo_password(self):
        response = self.client.post(
            "/api/auth/register/",
            {"username": "nick", "password": "sup3r-secret-pw"},
            format="json",
        )
        self.assertNotIn("password", response.data)

    def test_register_rejects_weak_password(self):
        response = self.client.post(
            "/api/auth/register/", {"username": "nick", "password": "123"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)
        self.assertFalse(User.objects.exists())

    def test_register_rejects_duplicate_username(self):
        User.objects.create_user(username="nick", password="pass")
        response = self.client.post(
            "/api/auth/register/", {"username": "nick", "password": "sup3r-secret-pw"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)
        self.assertEqual(User.objects.count(), 1)


class MeTests(APITestCase):

    def setUp(self):
        self.nick = User.objects.create_user(username="nick", password="pass", email="nick@example.com")

    def test_me_returns_current_user(self):
        self.client.force_authenticate(user=self.nick)
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"id": self.nick.id, "username": "nick", "email": "nick@example.com"})

    def test_me_requires_authentication(self):
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)


class LoginTests(APITestCase):

    def setUp(self):
        User.objects.create_user(username="nick", password="sup3r-secret-pw")

    def test_login_sets_refresh_cookie(self):
        response = self.client.post(
            "/api/auth/login/", {"username": "nick", "password": "sup3r-secret-pw"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["username"], "nick")
        self.assertIn("refresh_token", response.cookies)

    # the access token from a login should actually open authenticated endpoints
    def test_access_token_authenticates_requests(self):
        login = self.client.post(
            "/api/auth/login/", {"username": "nick", "password": "sup3r-secret-pw"}, format="json"
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + login.data["access"])
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 200)

    def test_login_rejects_bad_password(self):
        response = self.client.post(
            "/api/auth/login/", {"username": "nick", "password": "wrong"}, format="json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("refresh_token", response.cookies)


class RefreshAndLogoutTests(APITestCase):

    def setUp(self):
        User.objects.create_user(username="nick", password="sup3r-secret-pw")
        self.client.post(
            "/api/auth/login/", {"username": "nick", "password": "sup3r-secret-pw"}, format="json"
        )  # leaves the refresh cookie on the test client

    def test_refresh_issues_new_access_token(self):
        response = self.client.post("/api/auth/token/refresh/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_refresh_without_cookie_is_rejected(self):
        self.client.cookies.clear()
        self.assertEqual(self.client.post("/api/auth/token/refresh/").status_code, 401)

    # after logging out the refresh token must be dead, not just cleared from the browser
    def test_logout_blacklists_refresh_token(self):
        self.assertEqual(self.client.post("/api/auth/logout/").status_code, 200)
        self.assertEqual(self.client.post("/api/auth/token/refresh/").status_code, 401)
