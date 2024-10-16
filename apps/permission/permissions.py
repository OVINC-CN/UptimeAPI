from rest_framework.permissions import BasePermission


class SuperuserPermission(BasePermission):
    """
    check superuser
    """

    # pylint: disable=W0236
    async def has_permission(self, request, view):
        return request.user.is_superuser

    # pylint: disable=W0236
    async def has_object_permission(self, request, view, obj):
        return request.user.is_superuser
