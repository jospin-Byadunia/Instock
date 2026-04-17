from django.urls import path, include
from rest_framework.routers import DefaultRouter    
from .views import itemViewSet, CategoryViewSet 

router = DefaultRouter()

router.register(r'item', itemViewSet, basename='item')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = router.urls
