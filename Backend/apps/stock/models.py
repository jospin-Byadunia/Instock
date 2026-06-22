from django.db import models
from django.core.exceptions import ValidationError
from apps.items.models import Item
from apps.accounts.models import CustomUser

class Warehouse(models.Model):
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="warehouses",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    location = models.TextField(blank=True, null=True)
    manager = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_warehouse_name_per_organization",
            )
        ]

    def clean(self):
        if self.manager and self.manager.organization_id != self.organization_id:
            raise ValidationError("Manager must belong to the same organization as the warehouse.")

    def __str__(self):
        return self.name

class Stock(models.Model):
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="stocks",
        null=True,
        blank=True,
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "item", "warehouse"],
                name="unique_stock_per_item_warehouse_organization",
            )
        ]

    def clean(self):
        if self.item.organization_id != self.organization_id:
            raise ValidationError("Item must belong to the same organization as the stock.")
        if self.warehouse.organization_id != self.organization_id:
            raise ValidationError("Warehouse must belong to the same organization as the stock.")

    def __str__(self):
        return f"{self.item.name} - {self.warehouse.name} ({self.quantity})"
