from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from users.serializers import RegisterSerializer, UserSerializer


def token_response(user, data=None, status_code=status.HTTP_200_OK):
    """Return the access token in the body, the refresh token in an HttpOnly cookie."""
    refresh = RefreshToken.for_user(user)

    response = Response({**(data or {}), "access": str(refresh.access_token)}, status=status_code)
    response.set_cookie(
        key="refresh_token",
        value=str(refresh),
        httponly=True,
        secure=not settings.DEBUG,  # HTTPS only in production
        samesite="Lax",
        max_age=60 * 60 * 24,  # 1 day
    )
    return response


class RegisterView(APIView):
    permission_classes = []  # public endpoint, no auth required

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # sign the new user straight in, so they don't have to log in again
        return token_response(user, data={"user": UserSerializer(user).data}, status_code=status.HTTP_201_CREATED)


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LoginView(APIView):
    permission_classes = []  # public endpoint, no auth required

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is None:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        return token_response(user, data={"user": UserSerializer(user).data})


class RefreshView(APIView):
    permission_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"detail": "No refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            return Response({"access": str(refresh.access_token)})
        except Exception:
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                pass  # already invalid, no action needed

        response = Response({"detail": "Logged out"})
        response.delete_cookie("refresh_token")
        return response
