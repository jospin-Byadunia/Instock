from django.db import models
from apps.items.models import Item
from apps.accounts.models import CustomUser

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.TextField(blank=True, null=True)
    manager = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Stock(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ('item', 'warehouse')

    def __str__(self):
        return f"{self.item.name} - {self.warehouse.name} ({self.quantity})"
