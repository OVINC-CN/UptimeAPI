from django.db import models
from django.utils.translation import gettext_lazy
from ovinc_client.core.constants import SHORT_CHAR_LENGTH
from ovinc_client.core.models import BaseModel, ForeignKey, UniqIDField

from apps.monitor.constants import HTTPMethod, OnlineStatus


class ServiceStatus(BaseModel):
    """
    service status
    """

    id = models.BigAutoField(verbose_name=gettext_lazy("ID"), primary_key=True)
    service = ForeignKey(
        verbose_name=gettext_lazy("Service"), to="service.Service", related_name="status_dot", on_delete=models.CASCADE
    )
    timestamp = models.BigIntegerField(verbose_name=gettext_lazy("Timestamp(s)"))
    datetime = models.DateTimeField(verbose_name=gettext_lazy("Time"))
    status = models.SmallIntegerField(verbose_name=gettext_lazy("Status"), choices=OnlineStatus.choices)

    class Meta:
        verbose_name = gettext_lazy("Service Status")
        verbose_name_plural = verbose_name
        ordering = ["-id"]
        index_together = [
            ["service", "timestamp"],
        ]


class MonitorConfig(BaseModel):
    """
    monitor config
    """

    id = UniqIDField(verbose_name=gettext_lazy("ID"), primary_key=True)

    service = models.OneToOneField(
        verbose_name=gettext_lazy("Service"),
        to="service.Service",
        related_name="monitor_config",
        on_delete=models.CASCADE,
        db_constraint=False,
        db_index=True,
    )
    check_interval = models.IntegerField(verbose_name=gettext_lazy("Check Interval"))
    check_timeout = models.IntegerField(verbose_name=gettext_lazy("Check Timeout"))
    check_retry = models.IntegerField(verbose_name=gettext_lazy("Check Retry"))

    updated_by = ForeignKey(
        verbose_name=gettext_lazy("Updated By"),
        to="account.User",
        related_name="updated_service",
        on_delete=models.PROTECT,
        db_index=True,
    )
    updated_at = models.DateTimeField(verbose_name=gettext_lazy("Updated At"), auto_now=True)
    created_by = ForeignKey(
        verbose_name=gettext_lazy("Created By"),
        to="account.User",
        related_name="created_service",
        on_delete=models.PROTECT,
        db_index=True,
    )
    created_at = models.DateTimeField(verbose_name=gettext_lazy("Created At"), auto_now_add=True, db_index=True)

    http_method = models.CharField(
        verbose_name=gettext_lazy("HTTP Method"),
        max_length=SHORT_CHAR_LENGTH,
        choices=HTTPMethod.choices,
        null=True,
        blank=True,
    )
    http_url = models.TextField(verbose_name=gettext_lazy("HTTP URL"), null=True, blank=True)
    http_headers = models.JSONField(verbose_name=gettext_lazy("HTTP Headers"), null=True, blank=True)
    http_check_status_code = models.IntegerField(
        verbose_name=gettext_lazy("HTTP Success Status Code"), null=True, blank=True
    )

    class Meta:
        verbose_name = gettext_lazy("Monitor Config")
        verbose_name_plural = verbose_name
        ordering = ["-id"]
