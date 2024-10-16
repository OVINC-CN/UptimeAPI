from rest_framework.routers import DefaultRouter

from apps.service.views import ServiceViewSet

router = DefaultRouter()
router.register("services", ServiceViewSet)

urlpatterns = router.urls
