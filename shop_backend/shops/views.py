from rest_framework.viewsets import ModelViewSet
from .models import Shop
from .serializers import ShopSerializer, ShopImportSerializer, ShopStateSerializer
from orders.serializers import OrderSerializer
from .permissions import IsAuthenticatedSupplier
from rest_framework.response import Response
from orders.models import Order
from django.db.models import Q
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

        serializer = super().get_serializer(queryset, many=True)
        return Response(serializer.data)


class ShopOrderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedSupplier]
    http_method_names = ['get']

    def get_queryset(self):
        shops = Shop.objects.filter(user=self.request.user)
        return Order.objects.filter(~Q(status='basket'), shop__in=shops)
        # return Order.objects.filter(shop__in=shops).annotate(
        #     total=(models.Sum(models.F('contents__quantity') * models.F('products__price'))))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({'results': 'There is no orders associated with shops you manage.'})

        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrderItemsSerializer(instance)
        return Response(serializer.data)


class OpenShopViewSet(ModelViewSet):
    queryset = Shop.objects.filter(is_closed=False)
    serializer_class = ShopSerializer
    http_method_names = ['get']
