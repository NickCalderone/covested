from django.urls import path
from users.views import RegisterView, MeView, LoginView, RefreshView, LogoutView

urlpatterns = [
	path("register/", RegisterView.as_view(), name="register"),
	path("me/", MeView.as_view(), name="me"),
	path("login/", LoginView.as_view(), name="login"),
	path("token/refresh/", RefreshView.as_view(), name="token_refresh"),
	path("logout/", LogoutView.as_view(), name="logout"),
]
