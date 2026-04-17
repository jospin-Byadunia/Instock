from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):

        if request.path in ["/api/auth/login/", "/api/auth/refresh/"]:
            return None

        token = request.COOKIES.get("access")
        if not token:
            return None

        try:
            validated_token = self.get_validated_token(token)
        except TokenError:
            return None

        user = self.get_user(validated_token)
        return (user, validated_token)