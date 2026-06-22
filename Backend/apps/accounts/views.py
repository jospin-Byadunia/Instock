from rest_framework import generics, permissions, viewsets
from .permissions import IsOrganizationAdmin
from .serializers import (
    CustomUserSerializer,
    OrganizationSerializer,
    OrganizationSubscriptionSerializer,
    SubscriptionPlanSerializer,
)
from .models import CustomUser as User, Organization, OrganizationSubscription, SubscriptionPlan

class UserListView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.select_related("organization").order_by("username")

        if user.is_superuser:
            return queryset

        if not user.organization:
            return queryset.none()

        return queryset.filter(organization=user.organization)


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [IsOrganizationAdmin()]

    def get_queryset(self):
        user = self.request.user
        queryset = Organization.objects.select_related("owner").order_by("name")

        if user.is_superuser:
            return queryset

        if not user.organization:
            return queryset.none()

        return queryset.filter(id=user.organization_id)


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionPlanSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = SubscriptionPlan.objects.all().order_by("price", "max_accounts")
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(is_active=True)


class OrganizationSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSubscriptionSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [IsOrganizationAdmin()]

    def get_queryset(self):
        user = self.request.user
        queryset = OrganizationSubscription.objects.select_related(
            "organization",
            "plan",
        )

        if user.is_superuser:
            return queryset

        if not user.organization:
            return queryset.none()

        return queryset.filter(organization=user.organization)
