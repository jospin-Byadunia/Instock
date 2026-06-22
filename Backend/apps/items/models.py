from django.db import models
from django.core.exceptions import ValidationError

class Category(models.Model):
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="categories",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_category_name_per_organization",
            )
        ]

    def __str__(self):
        return self.name

class Item(models.Model):
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="items",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0) 

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "sku"],
                name="unique_item_sku_per_organization",
            )
        ]

    def clean(self):
        if self.category and self.category.organization_id != self.organization_id:
            raise ValidationError("Category must belong to the same organization as the item.")

    def __str__(self):
        return f"{self.name} ({self.sku})"
