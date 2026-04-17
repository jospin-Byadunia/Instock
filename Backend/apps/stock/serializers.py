from rest_framework import serializers
from .models import Stock, Warehouse
from apps.items.serializers import ItemSerializer

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)

    class Meta:
        model = Stock
        fields = '__all__'

class StockCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['item', 'warehouse', 'quantity']
