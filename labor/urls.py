from rest_framework.routers import DefaultRouter
from labor.views import LaborViewSet

router = DefaultRouter()
router.register(r"labor", LaborViewSet, basename="labor")

urlpatterns = router.urls
