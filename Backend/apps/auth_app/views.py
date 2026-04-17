from urllib import response
from rest_framework import generics, permissions
from .serializers import RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import LoginSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import rest_framework.status as status

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        # update last login
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        # generate tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": getattr(user, "role", None),
            }
        }, status=status.HTTP_200_OK)
        response.delete_cookie("access")
        response.delete_cookie("refresh")

        # 🔐 ACCESS COOKIE
        response.set_cookie(
            key="access",
            value=str(access),
            httponly=True,
            secure=False,   # set True in production (HTTPS)
            samesite="Lax",
            max_age=60 * 15,  # 15 minutes
        )

        # 🔐 REFRESH COOKIE
        response.set_cookie(
            key="refresh",
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=60 * 60 * 24 * 7,  # 7 days
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
                secure=False,
                samesite="Lax",
            )

            return response

        except Exception:
            return Response({"error": "Invalid refresh token"}, status=401)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        permissions.IsAdminUser().has_permission(request, self)
        return super().post(request, *args, **kwargs)

class getMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
