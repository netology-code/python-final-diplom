from rest_framework.viewsets import ModelViewSet
from .models import Shop
from .serializers import ShopSerializer, ShopImportSerializer, ShopStateSerializer, ShopOrderSerializer, \
    ShopCategorySerializer
from .permissions import IsAuthenticatedSupplier
from rest_framework.response import Response
from orders.models import Order
from django.db import models
from orders.serializers import OrderItemsSerializer


class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    http_method_names = ['get']


class ShopImportViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopImportSerializer
    permission_classes = [IsAuthenticatedSupplier]
    http_method_names = ['post']


class ShopStateViewSet(ModelViewSet):
    serializer_class = ShopStateSerializer
    permission_classes = [IsAuthenticatedSupplier]
    http_method_names = ['get', 'put']

    def get_queryset(self):
        return Shop.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({'results': 'There is no shops associated with your account.'})

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ShopOrderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedSupplier]
    http_method_names = ['get']

    def get_queryset(self):
        shops = Shop.objects.filter(user=self.request.user)
        if self.kwargs.get('pk'):
            return Order.objects.filter(shop__in=shops).annotate(
                total=(models.Sum(models.F('contents__quantity') * models.F('products__price'))))

        return shops

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({'results': 'There is no orders associated with shops you manage.'})

        serializer = ShopOrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrderItemsSerializer(instance)
        return Response(serializer.data)


class ShopCategoryViewSet(ModelViewSet):
    queryset = Shop.objects.prefetch_related('categories')
    serializer_class = ShopCategorySerializer
    http_method_names = ['get']
