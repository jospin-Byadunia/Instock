from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.stock.models import Warehouse
from .services import stock_in, stock_out
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from apps.items.models import Item
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.decorators import action
from .serializers import StockSerializer, StockCreateSerializer, WarehouseSerializer
from .models import Stock

class StockInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item")
        # quantity = request.data.get("quantity")
        quantity = int(request.data.get("quantity", 1))
        warehouse_id = request.data.get("warehouse")
        note = request.data.get("note", "")

        item = get_object_or_404(Item, id=item_id)
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)

        stock_obj = stock_in(
            item=item,
            warehouse=warehouse,
            quantity=quantity,
            user=request.user,
            note=note
        )

        serializer = StockSerializer(stock_obj)
        return Response(
    {
        "message": "Item added successfully",
        "data": StockSerializer(stock_obj).data
    },
    status=status.HTTP_201_CREATED,
)
    def get(self, request):
        stocks = Stock.objects.all()
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StockOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item")
        quantity = int(request.data.get("quantity", 1))
        warehouse_id = request.data.get("warehouse")
        note = request.data.get("note")

        if not item_id or not quantity or not warehouse_id:
            return Response(
                {"error": "item_id and quantity are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        item = get_object_or_404(Item, id=item_id)
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)

        try:
            stock_out(
                item=item,
                warehouse=warehouse,
                quantity=quantity,
                user=request.user,
                note=note
            )
        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Item removed successfully"},
            status=status.HTTP_200_OK
        )
        
class StockViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        stocks = Stock.objects.select_related("item", "warehouse")
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)
    
class WarehouseViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WarehouseSerializer
    queryset = Warehouse.objects.all()