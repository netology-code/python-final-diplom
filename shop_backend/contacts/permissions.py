from rest_framework.permissions import BasePermission


class IsAuthenticatedClient(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and not (request.user.is_supplier or request.user.is_staff))

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
