from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationSubscriptionViewSet,
    OrganizationViewSet,
    SubscriptionPlanViewSet,
    UserListView,
)

router = DefaultRouter()
router.register("organizations", OrganizationViewSet, basename="organization")
router.register("plans", SubscriptionPlanViewSet, basename="subscription-plan")
router.register(
    "subscriptions",
    OrganizationSubscriptionViewSet,
    basename="organization-subscription",
)

urlpatterns = [
    path("users/", UserListView.as_view(), name="user_list"),
    path("", include(router.urls)),
]
