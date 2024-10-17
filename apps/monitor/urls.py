from rest_framework.routers import DefaultRouter

from apps.monitor.views import MonitorConfigViewSet, ServiceStatusViewSet

router = DefaultRouter()
router.register("monitor_configs", MonitorConfigViewSet)
router.register("service_statuses", ServiceStatusViewSet)

urlpatterns = router.urls
