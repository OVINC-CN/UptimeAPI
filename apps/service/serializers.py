from adrf.serializers import ModelSerializer, Serializer
from channels.db import database_sync_to_async
from django.utils.translation import gettext, gettext_lazy
from ovinc_client.core.async_tools import SyncRunner
from ovinc_client.core.constants import SHORT_CHAR_LENGTH
from rest_framework import serializers

from apps.monitor.constants import OnlineStatus
from apps.service.models import Service


class SerializerMethodField(serializers.SerializerMethodField):
    async def ato_representation(self, *args, **kwargs):
        return super().to_representation(*args, **kwargs)


# pylint: disable=R0901
class ServiceInfoSerializer(ModelSerializer):
    status = SerializerMethodField()
    status_msg = SerializerMethodField()

    class Meta:
        model = Service
        fields = ["id", "name", "status", "status_msg"]

    def get_status(self, service: Service):
        status = self.context.get("recent_status", {}).get(service.id, None)
        if status:
            return status.status
        return OnlineStatus.UNKNOWN

    def get_status_msg(self, service: Service):
        status = self.context.get("recent_status", {}).get(service.id, None)
        if status and self.context.get("is_superuser", False):
            return status.status_msg
        return ""


class ServiceRequestSerializer(Serializer):
    keyword = serializers.CharField(
        label=gettext_lazy("Search Keyword"),
        max_length=SHORT_CHAR_LENGTH,
        required=False,
        allow_null=True,
        allow_blank=True,
    )


class CreateServiceSerializer(Serializer):
    name = serializers.CharField(label=gettext_lazy("Service Name"), max_length=SHORT_CHAR_LENGTH)

    def validate_name(self, name: str) -> str:
        if SyncRunner().run(self.check_name_exist(name)):
            raise serializers.ValidationError(gettext("Service with name '%s' already exists") % name)
        return name

    @database_sync_to_async
    def check_name_exist(self, name: str):
        return Service.objects.filter(name=name).exists()


class UpdateServiceSerializer(CreateServiceSerializer, ModelSerializer):
    class Meta:
        model = Service
        fields = ["name"]

    @database_sync_to_async
    def check_name_exist(self, name: str):
        return Service.objects.filter(name=name).exclude(id=self.instance.id).exists()
