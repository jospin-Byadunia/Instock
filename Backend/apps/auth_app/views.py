from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.permissions import IsOrganizationAdmin
from .serializers import (
    LoginSerializer,
    OrganizationSignupSerializer,
    RegisterSerializer,
    UserSerializer,
)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response(
            {
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": getattr(user, "role", None),
                    "organization": user.organization_id,
                    "organization_slug": user.organization.slug if user.organization else None,
                },
            },
            status=status.HTTP_200_OK,
        )
        response.delete_cookie("access")
        response.delete_cookie("refresh")

        response.set_cookie(
            key="access",
            value=str(access),
            httponly=True,
            secure=True,
            samesite="none",
            max_age=60 * 15,
        )
        response.set_cookie(
            key="refresh",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="none",
            max_age=60 * 60 * 24 * 7,
        )

        return response


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        response = Response({"detail": "Logout successful"})
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response


class RefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh")

        if not refresh_token:
            return Response({"error": "No refresh token"}, status=401)

        try:
            refresh = RefreshToken(refresh_token)
            access = refresh.access_token

            response = Response({"message": "Token refreshed"})
            response.set_cookie(
                key="access",
                value=str(access),
                httponly=True,
                secure=True,
                samesite="none",
            )

            return response

        except Exception:
            return Response({"error": "Invalid refresh token"}, status=401)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsOrganizationAdmin]


class OrganizationSignupView(generics.CreateAPIView):
    serializer_class = OrganizationSignupSerializer
    permission_classes = [permissions.AllowAny]


class getMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
