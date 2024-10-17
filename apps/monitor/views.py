from channels.db import database_sync_to_async
from django.db.models import Q
from django.utils.translation import gettext
from ovinc_client.core.viewsets import (
    CreateMixin,
    DestroyMixin,
    ListMixin,
    MainViewSet,
    RetrieveMixin,
    UpdateMixin,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.monitor.constants import CheckType, HTTPMethod, OnlineStatus
from apps.monitor.models import MonitorConfig, ServiceStatus
from apps.monitor.serializers import (
    HTTPMonitorConfigSerializer,
    ListServiceStatusSerializer,
    MonitoConfigSearchSerializer,
    MonitorConfigBaseSerializer,
    MonitorConfigInfoSerializer,
    MonitorConfigListSerializer,
    ServiceStatusListSerializer,
)
from apps.service.models import Service
from apps.service.permissions import PublicServicePermission, SuperuserPermission
from common.utils import choices_to_list


# pylint: disable=R0901
class MonitorConfigViewSet(ListMixin, RetrieveMixin, CreateMixin, UpdateMixin, DestroyMixin, MainViewSet):
    """
    monitor viewset
    """

    queryset = MonitorConfig.objects.all()
    permission_classes = [SuperuserPermission]

    async def list(self, request, *args, **kwargs):
        """
        list monitor config
        """

        # validate request
        request_serializer = MonitoConfigSearchSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        # build filter
        condition = Q()
        if request_data.get("keyword"):
            condition &= Q(service__name__icontains=request_data.get("keyword"))
        if request_data.get("is_enabled") is not None:
            condition &= Q(is_enabled=request_data.get("is_enabled"))

        # search
        queryset = MonitorConfig.objects.filter(condition).prefetch_related("service")

        return Response(data=await MonitorConfigListSerializer(instance=queryset, many=True).adata)

    async def retrieve(self, request, *args, **kwargs):
        """
        load monitor config detail
        """

        config: MonitorConfig = await database_sync_to_async(self.get_object)()
        configs = MonitorConfig.objects.filter(id=config.id).prefetch_related("service")
        data = await MonitorConfigInfoSerializer(configs, many=True).adata
        return Response(data=data[0])

    async def create(self, request, *args, **kwargs):
        """
        create monitor config
        """

        return await self.update_or_create(None, request, *args, **kwargs)

    async def update(self, request, *args, **kwargs):
        """
        update monitor config
        """

        config: MonitorConfig = await database_sync_to_async(self.get_object)()
        return await self.update_or_create(config, request, *args, **kwargs)

    async def update_or_create(self, config, request, *args, **kwargs):
        """
        update or create monitor config
        """

        if config:
            request.data["service_id"] = config.service_id

        # pre validate
        pre_serializer = MonitorConfigBaseSerializer(data=request.data)
        pre_serializer.is_valid(raise_exception=True)

        # validate
        match pre_serializer.validated_data["check_type"]:
            case CheckType.HTTP:
                request_serializer = HTTPMonitorConfigSerializer(instance=config, data=request.data)
                request_serializer.is_valid(raise_exception=True)
            case _:
                raise ValueError(gettext("invalid check type %s") % pre_serializer.validated_data["check_type"])

        # save to db
        config = await request_serializer.asave(updated_by=request.user, created_by=request.user)

        # response
        configs = MonitorConfig.objects.filter(id=config.id).prefetch_related("service")
        data = await MonitorConfigInfoSerializer(configs, many=True).adata
        return Response(data=data[0])

    async def destroy(self, request, *args, **kwargs):
        """
        delete monitor config
        """

        config = await database_sync_to_async(self.get_object)()
        await database_sync_to_async(config.delete)()
        return Response()

    @action(methods=["GET"], detail=False)
    def common(self, request, *args, **kwargs):
        """
        common constants
        """

        return Response(
            data={
                "check_type": choices_to_list(CheckType),
                "online_status": choices_to_list(OnlineStatus),
                "http_method": choices_to_list(HTTPMethod),
            }
        )


class ServiceStatusViewSet(RetrieveMixin, MainViewSet):
    """
    service status viewset
    """

    queryset = Service.objects.all()
    permission_classes = [PublicServicePermission]

    async def retrieve(self, request, *args, **kwargs):
        """
        list service status points
        """

        # validate
        request_serializer = ListServiceStatusSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        # service inst
        service = await database_sync_to_async(self.get_object)()

        # load data points
        status_points = ServiceStatus.objects.filter(
            service=service, timestamp__range=[request_data["start_time"], request_data["end_time"]]
        ).order_by("timestamp")
        points_data = await ServiceStatusListSerializer(
            instance=status_points, many=True, context={"is_superuser": request.user.is_superuser}
        ).adata

        # response
        return Response(data=points_data)
