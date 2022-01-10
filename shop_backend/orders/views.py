from rest_framework.viewsets import ModelViewSet
from .models import Order
from .serializers import OrderSerializer
from contacts.permissions import IsAuthenticatedClient


class BasketViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedClient]
    http_method_names = ['post', 'get', 'put', 'delete']


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedClient]
    http_method_names = ['get']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
