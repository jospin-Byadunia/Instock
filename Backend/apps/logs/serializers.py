from rest_framework import serializers
from .models import StockLog

class StockLogSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    performed_by = serializers.StringRelatedField()

    class Meta:
        model = StockLog
        fields = [
            "id",
            "item",
            "item_name",
            "quantity",
            "action",
            "performed_by",
            "note",
            "created_at",
        ]
        read_only_fields = fields
