from rest_framework.viewsets import ModelViewSet
from .models import Order
from .serializers import BasketSerializer, OrderSerializer
from contacts.permissions import IsAuthenticatedClient
from django.db.models import Q
from rest_framework.response import Response


class BasketViewSet(ModelViewSet):
    serializer_class = BasketSerializer
    permission_classes = [IsAuthenticatedClient]
    http_method_names = ['post', 'get', 'put', 'delete']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, status='basket')

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'new'
        instance.save()
        serializer = OrderSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        super().perform_update(serializer)

        return Response(serializer.data)


class UserOrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedClient]
    http_method_names = ['get']

    def get_queryset(self):
        return Order.objects.prefetch_related('products').filter(~Q(status='basket'), user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = BasketSerializer(instance)
        return Response(serializer.data)
