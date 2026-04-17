from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockInView, StockOutView, StockViewSet, WarehouseViewSet

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'stock', StockViewSet, basename='stock')

urlpatterns = [
    path('stock/in/', StockInView.as_view(), name='stock-in'),
    path('stock/out/', StockOutView.as_view(), name='stock-out'),
    path('', include(router.urls)),
]
