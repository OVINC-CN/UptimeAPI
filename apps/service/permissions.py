from rest_framework.permissions import BasePermission


class SuperuserPermission(BasePermission):
    """
    superuser
    """

    def has_permission(self, request, view):
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser


class PublicServicePermission(SuperuserPermission):
    """
    public service or superuser
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if obj.is_public:
            return True
        return super().has_object_permission(request, view, obj)
