from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import StockLog
from .serializers import StockLogSerializer

class StockLogViewSet(ReadOnlyModelViewSet):
    serializer_class = StockLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        qs = StockLog.objects.select_related(
            "organization",
            "item",
            "performed_by"
        )

        if user.is_superuser:
            return qs

        if not user.organization:
            return qs.none()

        return qs.filter(organization=user.organization)
