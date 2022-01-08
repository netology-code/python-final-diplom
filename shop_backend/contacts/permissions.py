from rest_framework.permissions import BasePermission


class IsAuthenticatedClient(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and not (request.is_supplier or request.is_staff))
