from django.db import models
from apps.items.models import Item
from django.conf import settings

class StockLog(models.Model):
    ACTION_CHOICES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out')
    ]
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    sku = models.CharField(max_length=100, null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
)

    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.action.upper()} - {self.item.name} ({self.quantity})"
