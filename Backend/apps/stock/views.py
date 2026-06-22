from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.views import APIView

from .models import Stock, Warehouse
from .serializers import StockCreateSerializer, StockSerializer, WarehouseSerializer
from .services import stock_in, stock_out


def organization_queryset(queryset, user):
    if user.is_superuser:
        return queryset
    if not user.organization:
        return queryset.none()
    return queryset.filter(organization=user.organization)


class StockInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StockCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        note = request.data.get("note", "")

        stock_obj = stock_in(
            item=serializer.validated_data["item"],
            warehouse=serializer.validated_data["warehouse"],
            quantity=serializer.validated_data["quantity"],
            user=request.user,
            note=note,
        )

        return Response(
            {
                "message": "Item added successfully",
                "data": StockSerializer(stock_obj, context={"request": request}).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        stocks = organization_queryset(
            Stock.objects.select_related("organization", "item", "warehouse"),
            request.user,
        )
        serializer = StockSerializer(stocks, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class StockOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StockCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        note = request.data.get("note")

        try:
            stock_out(
                item=serializer.validated_data["item"],
                warehouse=serializer.validated_data["warehouse"],
                quantity=serializer.validated_data["quantity"],
                user=request.user,
                note=note,
            )
        except Stock.DoesNotExist:
            return Response(
                {"error": "Stock record does not exist for this item and warehouse."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Item removed successfully"},
            status=status.HTTP_200_OK,
        )


class StockViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        stocks = organization_queryset(
            Stock.objects.select_related("organization", "item", "warehouse"),
            request.user,
        )
        serializer = StockSerializer(stocks, many=True, context={"request": request})
        return Response(serializer.data)


class WarehouseViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WarehouseSerializer

    def get_queryset(self):
        return organization_queryset(
            Warehouse.objects.select_related("organization", "manager"),
            self.request.user,
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
