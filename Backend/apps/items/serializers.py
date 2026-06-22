from rest_framework import serializers
from .models import Item, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['organization']

class ItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.none(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ['organization']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            if user.is_superuser:
                self.fields["category_id"].queryset = Category.objects.all()
            elif user.organization:
                self.fields["category_id"].queryset = Category.objects.filter(
                    organization=user.organization
                )

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        organization = getattr(self.instance, "organization", None)

        if user and user.is_authenticated and not user.is_superuser:
            organization = user.organization

        category = attrs.get("category", getattr(self.instance, "category", None))
        if category and organization and category.organization_id != organization.id:
            raise serializers.ValidationError(
                {"category_id": "Category must belong to your organization."}
            )

        return attrs
