from django.test import TestCase

from apps.accounts.models import Organization
from apps.items.models import Item
from apps.reports.services import export_table


class ReportExportTests(TestCase):
    def test_export_table_filters_rows_by_organization(self):
        acme = Organization.objects.create(name="Acme", slug="acme")
        beta = Organization.objects.create(name="Beta", slug="beta")
        Item.objects.create(
            organization=acme,
            name="Cable",
            sku="ACME-CABLE",
            unit="pcs",
        )
        Item.objects.create(
            organization=beta,
            name="Bolt",
            sku="BETA-BOLT",
            unit="pcs",
        )

        csv_data = export_table("Item", app_name="items", organization=acme)

        self.assertIn("ACME-CABLE", csv_data)
        self.assertNotIn("BETA-BOLT", csv_data)
