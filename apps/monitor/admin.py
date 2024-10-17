from django.contrib import admin

from apps.monitor.models import MonitorConfig, ServiceStatus
from common.admin import NicknameMixinAdmin


@admin.register(ServiceStatus)
class ServiceStatusAdmin(admin.ModelAdmin):
    list_display = ["id", "service", "duration", "status", "status_msg", "datetime"]
    list_filter = ["service"]


@admin.register(MonitorConfig)
class MonitorConfigAdmin(NicknameMixinAdmin, admin.ModelAdmin):
    list_display = [
        "service",
        "check_interval",
        "check_timeout",
        "check_retry",
        "is_enabled",
        "updated_by_username",
        "updated_at",
        "created_by_username",
        "created_at",
    ]
    list_filter = ["service", "is_enabled"]
