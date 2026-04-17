from django.urls import path
from .views import LoginView, RefreshTokenView, RegisterView, getMeView, LogoutView


urlpatterns = [
     path('register/', RegisterView.as_view(), name='register'),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("me/", getMeView.as_view(), name="get_me"),
    
]