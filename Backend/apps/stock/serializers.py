from rest_framework import serializers
from .models import Stock, Warehouse
from apps.accounts.models import CustomUser
from apps.items.models import Item
from apps.items.serializers import ItemSerializer

class WarehouseSerializer(serializers.ModelSerializer):
    manager = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.none(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Warehouse
        fields = '__all__'
        read_only_fields = ['organization']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            if user.is_superuser:
                self.fields["manager"].queryset = CustomUser.objects.all()
            elif user.organization:
                self.fields["manager"].queryset = CustomUser.objects.filter(
                    organization=user.organization
                )

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        organization = getattr(self.instance, "organization", None)

        if user and user.is_authenticated and not user.is_superuser:
            organization = user.organization

        manager = attrs.get("manager", getattr(self.instance, "manager", None))
        if manager and organization and manager.organization_id != organization.id:
            raise serializers.ValidationError(
                {"manager": "Manager must belong to your organization."}
            )

        return attrs

class StockSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)

    class Meta:
        model = Stock
        fields = '__all__'
        read_only_fields = ['organization']

class StockCreateSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.none())
    warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.none())
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = Stock
        fields = ['item', 'warehouse', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            if user.is_superuser:
                self.fields["item"].queryset = Item.objects.all()
                self.fields["warehouse"].queryset = Warehouse.objects.all()
            elif user.organization:
                self.fields["item"].queryset = Item.objects.filter(
                    organization=user.organization
                )
                self.fields["warehouse"].queryset = Warehouse.objects.filter(
                    organization=user.organization
                )

    def validate(self, attrs):
        item = attrs.get("item")
        warehouse = attrs.get("warehouse")
        if item and warehouse and item.organization_id != warehouse.organization_id:
            raise serializers.ValidationError(
                "Item and warehouse must belong to the same organization."
            )
        return attrs
