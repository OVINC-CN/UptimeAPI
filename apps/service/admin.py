from django.contrib import admin

from apps.service.models import Service
from common.admin import NicknameMixinAdmin


@admin.register(Service)
class ServiceAdmin(NicknameMixinAdmin, admin.ModelAdmin):
    list_display = ["name", "updated_by_username", "updated_at", "created_by_username", "created_at"]
    search_fields = ["name"]
    ordering = ["name"]
