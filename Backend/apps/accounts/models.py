from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Organization(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    owner = models.ForeignKey(
        "CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_organizations",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_active_subscription(self):
        now = timezone.now()
        return (
            self.subscriptions.select_related("plan")
            .filter(
                status__in=[
                    OrganizationSubscription.Status.ACTIVE,
                    OrganizationSubscription.Status.TRIALING,
                ],
                current_period_start__lte=now,
                current_period_end__gte=now,
            )
            .order_by("-current_period_end")
            .first()
        )

    @property
    def active_subscription(self):
        return self.get_active_subscription()

    @property
    def account_limit(self):
        subscription = self.get_active_subscription()
        return subscription.account_limit if subscription else 0

    @property
    def active_user_count(self):
        return self.users.filter(is_active=True).count()

    @property
    def seats_available(self):
        return max(self.account_limit - self.active_user_count, 0)

    def has_available_seat(self):
        return self.is_active and self.account_limit > self.active_user_count


class SubscriptionPlan(models.Model):
    class BillingInterval(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        YEARLY = "yearly", "Yearly"

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    max_accounts = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    billing_interval = models.CharField(
        max_length=20,
        choices=BillingInterval.choices,
        default=BillingInterval.MONTHLY,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["price", "max_accounts"]

    def __str__(self):
        return f"{self.name} ({self.max_accounts} accounts)"


class OrganizationSubscription(models.Model):
    class Status(models.TextChoices):
        TRIALING = "trialing", "Trialing"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past due"
        CANCELED = "canceled", "Canceled"
        EXPIRED = "expired", "Expired"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    current_period_start = models.DateTimeField(default=timezone.now)
    current_period_end = models.DateTimeField()
    external_reference = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-current_period_end"]

    def __str__(self):
        return f"{self.organization} - {self.plan}"

    @property
    def account_limit(self):
        return self.plan.max_accounts

    @property
    def is_current(self):
        now = timezone.now()
        return (
            self.status in [self.Status.ACTIVE, self.Status.TRIALING]
            and self.current_period_start <= now <= self.current_period_end
        )

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
    )
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('Depot Manager', 'Depot Manager'),
    ]
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='staff')

    def __str__(self):
        return self.username
