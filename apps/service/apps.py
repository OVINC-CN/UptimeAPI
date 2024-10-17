from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class ServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.service"
    verbose_name = gettext_lazy("Service Module")
