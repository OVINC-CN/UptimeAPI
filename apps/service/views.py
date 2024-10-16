from channels.db import database_sync_to_async
from django.db.models import Q
from ovinc_client.core.viewsets import (
    CreateMixin,
    DestroyMixin,
    ListMixin,
    MainViewSet,
    UpdateMixin,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.monitor.models import MonitorConfig
from apps.monitor.serializers import MonitorConfigInfoSerializer
from apps.permission.permissions import SuperuserPermission
from apps.service.models import Service
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
        if request_data.get("keyword"):
            condition &= Q(name__icontains=request_data.get("keyword"))

        # load from db
        queryset = Service.objects.filter(condition).prefetch_related("updated_by", "created_by")

        # response
        return Response(data=await ServiceInfoSerializer(instance=queryset, many=True).adata)

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
