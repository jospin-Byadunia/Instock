from rest_framework import serializers
from .models import CustomUser, Organization, OrganizationSubscription, SubscriptionPlan


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            "id",
            "name",
            "slug",
            "max_accounts",
            "price",
            "billing_interval",
            "is_active",
        ]


class OrganizationSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.filter(is_active=True),
        source="plan",
        write_only=True,
    )
    account_limit = serializers.IntegerField(read_only=True)
    is_current = serializers.BooleanField(read_only=True)

    class Meta:
        model = OrganizationSubscription
        fields = [
            "id",
            "organization",
            "plan",
            "plan_id",
            "status",
            "current_period_start",
            "current_period_end",
            "account_limit",
            "is_current",
            "external_reference",
        ]


class OrganizationSerializer(serializers.ModelSerializer):
    active_subscription = serializers.SerializerMethodField()
    account_limit = serializers.IntegerField(read_only=True)
    active_user_count = serializers.IntegerField(read_only=True)
    seats_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "owner",
            "is_active",
            "active_subscription",
            "account_limit",
            "active_user_count",
            "seats_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_active_subscription(self, obj):
        subscription = obj.active_subscription
        if not subscription:
            return None
        return OrganizationSubscriptionSerializer(subscription).data

class CustomUserSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'role',
            'phone_number',
            'organization',
            'organization_name',
            'is_active',
            'date_joined',
        ]
        read_only_fields = ['date_joined']
