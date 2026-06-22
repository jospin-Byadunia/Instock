from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    OrganizationSignupView,
    RefreshTokenView,
    RegisterView,
    getMeView,
)


urlpatterns = [
    path('organizations/signup/', OrganizationSignupView.as_view(), name='organization-signup'),
    path('register/', RegisterView.as_view(), name='register'),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("me/", getMeView.as_view(), name="get_me"),
    
]
