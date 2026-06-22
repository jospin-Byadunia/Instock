from rest_framework import viewsets, permissions
from .models import Item, Category
from .serializers import ItemSerializer, CategorySerializer



class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Item.objects.select_related("organization", "category").order_by('-created_at')
        user = self.request.user

        if user.is_superuser:
            return queryset

        if not user.organization:
            return queryset.none()

        return queryset.filter(organization=user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Category.objects.select_related("organization").order_by('name')
        user = self.request.user

        if user.is_superuser:
            return queryset

        if not user.organization:
            return queryset.none()

        return queryset.filter(organization=user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

