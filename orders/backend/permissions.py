from rest_framework import permissions


class IsShopUser(permissions.BasePermission):
    message = 'Only for shops'

    def has_permission(self, request, view):
        return request.user.type == 'shop'
