from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class MonitorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.monitor"
    verbose_name = gettext_lazy("Monitor Module")
