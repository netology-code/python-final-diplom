from shops.models import Shop
from rest_framework.viewsets import ModelViewSet
from .serializers import ShopImportSerializer, OrdersStateSerializer
from rest_framework.permissions import IsAuthenticated


class ShopImportViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopImportSerializer
    http_method_names = ['post']
    permission_classes = [IsAuthenticated]


class OrdersStateViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = OrdersStateSerializer
    http_method_names = ['get', 'post']
