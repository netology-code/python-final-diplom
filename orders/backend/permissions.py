from rest_framework import permissions
from rest_framework.permissions import IsAdminUser


class IsShopUser(permissions.BasePermission):
    message = 'Only for shops'

    def has_permission(self, request, view):
        return request.user.type == 'shop'


class CustomAdminUser(IsAdminUser):
    message = "Only for admin"
