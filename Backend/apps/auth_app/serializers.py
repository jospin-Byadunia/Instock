from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from apps.accounts.models import (
    CustomUser,
    Organization,
    OrganizationSubscription,
    SubscriptionPlan,
)


class UserSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    organization_slug = serializers.CharField(source="organization.slug", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "role",
            "phone_number",
            "organization",
            "organization_name",
            "organization_slug",
        ]


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["organization_id"] = user.organization_id
        token["organization_slug"] = user.organization.slug if user.organization else None
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        self.user.last_login = timezone.now()
        self.user.save(update_fields=["last_login"])

        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            refresh_token = RefreshToken(self.token)
            refresh_token.blacklist()
        except TokenError:
            raise serializers.ValidationError({"refresh": "Invalid or expired token"})


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True, label="Confirm Password")
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "password",
            "password2",
            "role",
            "phone_number",
            "organization",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        request = self.context.get("request")
        requester = getattr(request, "user", None)

        if requester and requester.is_authenticated and not requester.is_superuser:
            if requester.role != "admin":
                raise serializers.ValidationError(
                    {"detail": "Only organization admins can create users."}
                )
            if not requester.organization:
                raise serializers.ValidationError(
                    {"organization": "Your account is not linked to an organization."}
                )
            attrs["organization"] = requester.organization

        organization = attrs.get("organization")
        if organization:
            if not organization.active_subscription:
                raise serializers.ValidationError(
                    {"organization": "Organization does not have an active subscription."}
                )
            if not organization.has_available_seat():
                raise serializers.ValidationError(
                    {"organization": "Organization account limit has been reached."}
                )

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data.get("role", "staff"),
            phone_number=validated_data.get("phone_number"),
            organization=validated_data.get("organization"),
        )
        return user


class OrganizationSignupSerializer(serializers.Serializer):
    organization_name = serializers.CharField(max_length=255)
    organization_slug = serializers.SlugField(max_length=255, required=False)
    plan = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=SubscriptionPlan.objects.filter(is_active=True),
    )
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True, label="Confirm Password")
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        slug = attrs.get("organization_slug") or slugify(attrs["organization_name"])
        if not slug:
            raise serializers.ValidationError(
                {"organization_slug": "Organization slug is required."}
            )
        if Organization.objects.filter(slug=slug).exists():
            raise serializers.ValidationError(
                {"organization_slug": "An organization with this slug already exists."}
            )
        if CustomUser.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError(
                {"username": "A user with this username already exists."}
            )
        if CustomUser.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError(
                {"email": "A user with this email already exists."}
            )

        attrs["organization_slug"] = slug
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        plan = validated_data["plan"]
        now = timezone.now()
        period_days = (
            365
            if plan.billing_interval == SubscriptionPlan.BillingInterval.YEARLY
            else 30
        )

        organization = Organization.objects.create(
            name=validated_data["organization_name"],
            slug=validated_data["organization_slug"],
        )
        owner = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role="admin",
            phone_number=validated_data.get("phone_number", ""),
            organization=organization,
        )
        organization.owner = owner
        organization.save(update_fields=["owner"])

        OrganizationSubscription.objects.create(
            organization=organization,
            plan=plan,
            status=OrganizationSubscription.Status.ACTIVE,
            current_period_start=now,
            current_period_end=now + timedelta(days=period_days),
        )

        return {"organization": organization, "user": owner}

    def to_representation(self, instance):
        organization = instance["organization"]
        user = instance["user"]
        return {
            "organization": {
                "id": organization.id,
                "name": organization.name,
                "slug": organization.slug,
                "account_limit": organization.account_limit,
                "seats_available": organization.seats_available,
            },
            "user": UserSerializer(user).data,
        }
