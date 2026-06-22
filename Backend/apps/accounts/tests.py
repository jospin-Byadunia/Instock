from datetime import timedelta

from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import (
    CustomUser,
    Organization,
    OrganizationSubscription,
    SubscriptionPlan,
)


def create_organization(name="Acme", slug="acme", max_accounts=2):
    plan = SubscriptionPlan.objects.create(
        name=f"{name} Plan",
        slug=f"{slug}-plan",
        max_accounts=max_accounts,
        price=99,
    )
    organization = Organization.objects.create(name=name, slug=slug)
    owner = CustomUser.objects.create_user(
        username=f"{slug}-owner",
        email=f"{slug}-owner@example.com",
        password="Pass12345!",
        role="admin",
        organization=organization,
    )
    organization.owner = owner
    organization.save(update_fields=["owner"])
    now = timezone.now()
    OrganizationSubscription.objects.create(
        organization=organization,
        plan=plan,
        status=OrganizationSubscription.Status.ACTIVE,
        current_period_start=now - timedelta(days=1),
        current_period_end=now + timedelta(days=30),
    )
    return organization, owner


@override_settings(ALLOWED_HOSTS=["testserver", "localhost"])
class OrganizationSignupTests(APITestCase):
    def test_organization_signup_creates_tenant_owner_and_subscription(self):
        SubscriptionPlan.objects.create(
            name="Starter",
            slug="starter",
            max_accounts=3,
            price=49,
        )

        response = self.client.post(
            reverse("organization-signup"),
            {
                "organization_name": "North Depot",
                "organization_slug": "north-depot",
                "plan": "starter",
                "username": "north-admin",
                "email": "admin@north.example",
                "password": "Pass12345!",
                "password2": "Pass12345!",
                "phone_number": "+27110000000",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        organization = Organization.objects.get(slug="north-depot")
        owner = CustomUser.objects.get(username="north-admin")

        self.assertEqual(owner.organization, organization)
        self.assertEqual(owner.role, "admin")
        self.assertFalse(owner.is_staff)
        self.assertEqual(organization.owner, owner)
        self.assertEqual(organization.account_limit, 3)
        self.assertEqual(organization.seats_available, 2)
        self.assertTrue(organization.subscriptions.filter(status="active").exists())


@override_settings(ALLOWED_HOSTS=["testserver", "localhost"])
class AccountLimitTests(APITestCase):
    def test_org_admin_cannot_create_users_beyond_subscription_limit(self):
        organization, admin = create_organization(max_accounts=2)
        self.client.force_authenticate(admin)

        first_response = self.client.post(
            reverse("register"),
            {
                "username": "staff-1",
                "email": "staff1@example.com",
                "password": "Pass12345!",
                "password2": "Pass12345!",
                "role": "staff",
            },
            format="json",
        )
        second_response = self.client.post(
            reverse("register"),
            {
                "username": "staff-2",
                "email": "staff2@example.com",
                "password": "Pass12345!",
                "password2": "Pass12345!",
                "role": "staff",
            },
            format="json",
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(organization.users.filter(is_active=True).count(), 2)

    def test_org_admin_lists_only_users_in_their_organization(self):
        organization, admin = create_organization(name="Acme", slug="acme")
        other_organization, _ = create_organization(name="Beta", slug="beta")
        CustomUser.objects.create_user(
            username="acme-staff",
            email="acme-staff@example.com",
            password="Pass12345!",
            organization=organization,
        )
        CustomUser.objects.create_user(
            username="beta-staff",
            email="beta-staff@example.com",
            password="Pass12345!",
            organization=other_organization,
        )
        self.client.force_authenticate(admin)

        response = self.client.get("/api/v1/accounts/users/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = {user["username"] for user in response.data["results"]}
        self.assertIn("acme-owner", usernames)
        self.assertIn("acme-staff", usernames)
        self.assertNotIn("beta-owner", usernames)
        self.assertNotIn("beta-staff", usernames)
