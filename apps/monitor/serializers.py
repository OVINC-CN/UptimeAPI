from adrf.serializers import ModelSerializer, Serializer
from django.conf import settings
from django.utils.translation import gettext, gettext_lazy
from rest_framework import serializers

from apps.monitor.constants import HTTPMethod
from apps.monitor.models import MonitorConfig, ServiceStatus


# pylint: disable=R0901
class MonitorConfigInfoSerializer(ModelSerializer):
    service = serializers.CharField(source="service.id")
    service_name = serializers.CharField(source="service.name")

    class Meta:
        model = MonitorConfig
        exclude = ["updated_by", "updated_at", "created_by", "created_at"]


# pylint: disable=R0901
class MonitorConfigListSerializer(MonitorConfigInfoSerializer):
    class Meta:
        model = MonitorConfig
        fields = ["id", "service", "service_name", "is_enabled"]


class MonitoConfigSearchSerializer(Serializer):
    keyword = serializers.CharField(
        label=gettext_lazy("Search Keyword"), required=False, allow_blank=True, allow_null=True
    )
    is_enabled = serializers.BooleanField(label=gettext_lazy("Is Enabled"), required=False, allow_null=True)


# pylint: disable=R0901
class MonitorConfigBaseSerializer(ModelSerializer):
    service_id = serializers.CharField(label=gettext_lazy("Service"))
    check_interval = serializers.IntegerField(
        label=gettext_lazy("Check Interval (s)"),
        min_value=settings.MONITOR_CHECK_INTERVAL_MIN,
        max_value=settings.MONITOR_CHECK_INTERVAL_MAX,
    )
    check_timeout = serializers.IntegerField(
        label=gettext_lazy("Check Timeout (s)"),
        min_value=settings.MONITOR_CHECK_TIMEOUT_MIN,
        max_value=settings.MONITOR_CHECK_TIMEOUT_MAX,
    )
    check_retry = serializers.IntegerField(
        label=gettext_lazy("Check Retry"),
        min_value=settings.MONITOR_CHECK_RETRY_MIN,
        max_value=settings.MONITOR_CHECK_RETRY_MAX,
    )

    class Meta:
        model = MonitorConfig
        fields = ["service_id", "check_type", "check_interval", "check_timeout", "check_retry", "is_enabled"]


# pylint: disable=R0901
class HTTPMonitorConfigSerializer(MonitorConfigBaseSerializer):
    http_method = serializers.ChoiceField(label=gettext_lazy("HTTP Method"), choices=HTTPMethod.choices)
    http_url = serializers.URLField(label=gettext_lazy("HTTP URL"))
    http_headers = serializers.DictField(
        label=gettext_lazy("HTTP Headers"), default=dict, child=serializers.CharField()
    )
    http_follow_redirect = serializers.BooleanField(label=gettext_lazy("Follow Redirect"))
    http_check_status_code = serializers.IntegerField(label=gettext_lazy("HTTP Success Status Code"))

    class Meta:
        model = MonitorConfig
        fields = [
            *MonitorConfigBaseSerializer.Meta.fields,
            "http_method",
            "http_url",
            "http_headers",
            "http_follow_redirect",
            "http_check_status_code",
        ]


class ListServiceStatusSerializer(Serializer):
    start_time = serializers.IntegerField(label=gettext_lazy("Start Time"))
    end_time = serializers.IntegerField(label=gettext_lazy("End Time"))

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)
        if data["end_time"] - data["start_time"] > (settings.SVC_STATUS_MAX_TIME_RANGE_DAYS * 60 * 60 * 24):
            raise serializers.ValidationError(
                gettext("time range longer than %d days") % settings.SVC_STATUS_MAX_TIME_RANGE_DAYS
            )
        return data


class ServiceStatusListSerializer(ModelSerializer):
    duration = serializers.FloatField()

    class Meta:
        model = ServiceStatus
        fields = ["timestamp", "status", "status_msg", "duration"]

    async def ato_representation(self, instance: ServiceStatus) -> dict:
        data = await super().ato_representation(instance)
        if not self.context.get("is_superuser", False):
            data["status_msg"] = ""
        return data
