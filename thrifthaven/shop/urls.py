from rest_framework import routers
from .views import CategoryViewSet, ItemViewSet

router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'items', ItemViewSet)

urlpatterns = router.urls
