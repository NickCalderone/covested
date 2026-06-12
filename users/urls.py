from django.urls import path
from users.views import LoginView, RefreshView, LogoutView

urlpatterns = [
	path("login/", LoginView.as_view(), name="login"),
	path("token/refresh/", RefreshView.as_view(), name="token_refresh"),
	path("logout/", LogoutView.as_view(), name="logout"),
]