from rest_framework.permissions import BasePermission


class IsShop(BasePermission):
    """Разрешение действий над объектами типу пользователя 'Магазин'."""
    def has_permission(self, request, view):
        """Вернёт True, если пользователь принадлежит типу 'Магазин'."""
        return request.user.type == 'shop'

    def has_object_permission(self, request, view, obj): 
        """Вернёт True в случае, если метод запроса - 'GET'.
        Вернёт True в случае, если метод запроса - 'POST' и пользователь является создателем объекта.
        """
        if request.method == 'GET':
            return True 
        return request.user == obj.user
         