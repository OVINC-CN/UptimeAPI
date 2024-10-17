from typing import Dict

from channels.db import database_sync_to_async
from django.db.models import Max, Q, QuerySet
from ovinc_client.core.viewsets import (
    CreateMixin,
    DestroyMixin,
    ListMixin,
    MainViewSet,
    UpdateMixin,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.monitor.models import MonitorConfig, ServiceStatus
from apps.monitor.serializers import MonitorConfigInfoSerializer
from apps.service.models import Service
from apps.service.permissions import SuperuserPermission
from apps.service.serializers import (
    CreateServiceSerializer,
    ServiceInfoSerializer,
    ServiceRequestSerializer,
    UpdateServiceSerializer,
)


# pylint: disable=R0901
class ServiceViewSet(ListMixin, CreateMixin, UpdateMixin, DestroyMixin, MainViewSet):
    """
    service viewset
    """

    queryset = Service.objects.all()
    permission_classes = [SuperuserPermission]

    def get_permissions(self):
        if self.action in ["list"]:
            return []
        return super().get_permissions()

    async def list(self, request, *args, **kwargs):
        """
        service list
        """

        # validate request
        request_serializer = ServiceRequestSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        # build filter
        condition = Q()
        if not request.user.is_superuser:
            condition &= Q(is_public=True)
        if request_data.get("keyword"):
            condition &= Q(name__icontains=request_data.get("keyword"))

        # load from db
        queryset = Service.objects.filter(condition).prefetch_related("updated_by", "created_by")

        # load status
        record_map = await self.load_status_records(services=queryset)

        # response
        return Response(
            data=await ServiceInfoSerializer(
                instance=queryset,
                many=True,
                context={"recent_status": record_map, "is_superuser": request.user.is_superuser},
            ).adata
        )

    @database_sync_to_async
    def load_status_records(self, services: QuerySet) -> Dict[str, ServiceStatus]:
        """
        load service last status
        """

        records = ServiceStatus.objects.filter(
            id__in=[
                i["id"]
                for i in ServiceStatus.objects.filter(service__in=services)
                .values("service")
                .annotate(timestamp=Max("timestamp"), id=Max("id"))
                .order_by()
            ]
        )
        record_map = {}
        for record in records:
            if record.service_id not in record_map:
                record_map[record.service_id] = record
        return record_map

    async def create(self, request, *args, **kwargs):
        """
        create service
        """

        # validate request
        request_serializer = CreateServiceSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        # create
        service = await database_sync_to_async(Service.objects.create)(
            name=request_data["name"], updated_by=request.user, created_by=request.user
        )

        # response
        return Response(data=await ServiceInfoSerializer(instance=service).adata)

    async def update(self, request, *args, **kwargs):
        """
        update service
        """

        # load instance
        service = await database_sync_to_async(self.get_object)()

        # validate request
        request_serializer = UpdateServiceSerializer(instance=service, data=request.data)
        request_serializer.is_valid(raise_exception=True)

        # update
        await request_serializer.asave()
        service = Service.objects.filter(id=service.id).prefetch_related("updated_by", "created_by")

        # response
        data = await ServiceInfoSerializer(instance=service, many=True).adata
        return Response(data=data[0])

    async def destroy(self, request, *args, **kwargs):
        """
        delete service
        """

        service = await database_sync_to_async(self.get_object)()
        await database_sync_to_async(service.delete)()

        return Response()

    @action(methods=["GET"], detail=True)
    async def monitor_config(self, request, *args, **kwargs):
        """
        load service monitor config
        """

        service = await database_sync_to_async(self.get_object)()

        configs = MonitorConfig.objects.filter(service=service).prefetch_related("service")
        if not await database_sync_to_async(configs.count)():
            return Response()

        data = await MonitorConfigInfoSerializer(instance=configs, many=True).adata
        return Response(data=data[0])
