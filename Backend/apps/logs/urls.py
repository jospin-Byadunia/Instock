from rest_framework.routers import DefaultRouter
from .views import StockLogViewSet

router = DefaultRouter()
router.register("stock-logs", StockLogViewSet, basename="stock-log")

urlpatterns = router.urls
