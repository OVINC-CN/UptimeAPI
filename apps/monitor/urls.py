from rest_framework.routers import DefaultRouter

from apps.monitor.views import MonitorConfigViewSet

router = DefaultRouter()
router.register("monitor_configs", MonitorConfigViewSet)

urlpatterns = router.urls
