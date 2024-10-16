from django.db import models
from django.utils.translation import gettext_lazy
from ovinc_client.core.constants import SHORT_CHAR_LENGTH
from ovinc_client.core.models import BaseModel, ForeignKey, UniqIDField


# pylint:disable=R0801
class Service(BaseModel):
    """
    service
    """

    id = UniqIDField(verbose_name=gettext_lazy("ID"))
    name = models.CharField(verbose_name=gettext_lazy("Service Name"), max_length=SHORT_CHAR_LENGTH, unique=True)
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

    class Meta:
        verbose_name = gettext_lazy("Service")
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
