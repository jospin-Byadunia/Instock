from datetime import timedelta

from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import (
    CustomUser,
    Organization,
    OrganizationSubscription,
    SubscriptionPlan,
)
from apps.items.models import Item
from apps.logs.models import StockLog
from apps.stock.models import Stock, Warehouse


def create_organization(name, slug, max_accounts=5):
    plan = SubscriptionPlan.objects.create(
        name=f"{name} Plan",
        slug=f"{slug}-plan",
        max_accounts=max_accounts,
        price=99,
    )
    organization = Organization.objects.create(name=name, slug=slug)
    admin = CustomUser.objects.create_user(
        username=f"{slug}-admin",
        email=f"{slug}-admin@example.com",
        password="Pass12345!",
        role="admin",
        organization=organization,
    )
    organization.owner = admin
    organization.save(update_fields=["owner"])
    now = timezone.now()
    OrganizationSubscription.objects.create(
        organization=organization,
        plan=plan,
        status=OrganizationSubscription.Status.ACTIVE,
        current_period_start=now - timedelta(days=1),
        current_period_end=now + timedelta(days=30),
    )
    return organization, admin


@override_settings(ALLOWED_HOSTS=["testserver", "localhost"])
class TenantInventoryTests(APITestCase):
    def setUp(self):
        self.organization, self.admin = create_organization("Acme", "acme")
        self.other_organization, self.other_admin = create_organization("Beta", "beta")
        self.item = Item.objects.create(
            organization=self.organization,
            name="Cable",
            sku="ACME-CABLE",
            unit="pcs",
        )
        self.other_item = Item.objects.create(
            organization=self.other_organization,
            name="Bolt",
            sku="BETA-BOLT",
            unit="pcs",
        )
        self.warehouse = Warehouse.objects.create(
            organization=self.organization,
            name="Main Warehouse",
        )
        self.other_warehouse = Warehouse.objects.create(
            organization=self.other_organization,
            name="Other Warehouse",
        )
        self.client.force_authenticate(self.admin)

    def test_item_api_assigns_and_filters_by_user_organization(self):
        create_response = self.client.post(
            "/api/v1/items/item/",
            {
                "name": "Adapter",
                "sku": "ACME-ADAPTER",
                "unit": "pcs",
                "price": "10.00",
            },
            format="json",
        )
        list_response = self.client.get("/api/v1/items/item/")

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        created_item = Item.objects.get(sku="ACME-ADAPTER")
        self.assertEqual(created_item.organization, self.organization)

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        skus = {item["sku"] for item in list_response.data["results"]}
        self.assertIn("ACME-CABLE", skus)
        self.assertIn("ACME-ADAPTER", skus)
        self.assertNotIn("BETA-BOLT", skus)

    def test_stock_in_rejects_item_from_another_organization(self):
        response = self.client.post(
            "/api/v1/manage/stock/in/",
            {
                "item": self.other_item.id,
                "warehouse": self.warehouse.id,
                "quantity": 5,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Stock.objects.exists())
        self.assertFalse(StockLog.objects.exists())

    def test_stock_in_creates_organization_scoped_stock_and_log(self):
        response = self.client.post(
            "/api/v1/manage/stock/in/",
            {
                "item": self.item.id,
                "warehouse": self.warehouse.id,
                "quantity": 7,
                "note": "Initial load",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        stock = Stock.objects.get(item=self.item, warehouse=self.warehouse)
        log = StockLog.objects.get(item=self.item)
        self.assertEqual(stock.organization, self.organization)
        self.assertEqual(stock.quantity, 7)
        self.assertEqual(log.organization, self.organization)
        self.assertEqual(log.performed_by, self.admin)

    def test_stock_list_returns_only_current_organization_stock(self):
        Stock.objects.create(
            organization=self.organization,
            item=self.item,
            warehouse=self.warehouse,
            quantity=3,
        )
        Stock.objects.create(
            organization=self.other_organization,
            item=self.other_item,
            warehouse=self.other_warehouse,
            quantity=11,
        )

        response = self.client.get("/api/v1/manage/stock/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item_ids = {stock["item"]["id"] for stock in response.data}
        self.assertEqual(item_ids, {self.item.id})
