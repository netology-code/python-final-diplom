from rest_framework.permissions import BasePermission


class IsOnlyShop(BasePermission):
    """Разрешает доступ только магазинам"""

    def has_permission(self, request, view):
        return request.user.type == 'shop' and request.user
