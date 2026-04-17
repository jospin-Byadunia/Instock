from django.urls import path
from .views import StockLogExportView, WarehouseExportView, StockExportView, ItemExportView, CategoryExportView, UserExportView

urlpatterns = [
    path("stocklog/", StockLogExportView.as_view(), name="export-stocklog"),
    path("warehouse/", WarehouseExportView.as_view(), name="export-warehouse"),
    path("stock/", StockExportView.as_view(), name="export-stock"),
    path("item/", ItemExportView.as_view(), name="export-item"),    
    path("category/", CategoryExportView.as_view(), name="export-category"),
    path("user/", UserExportView.as_view(), name="export-user"),
]