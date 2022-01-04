from rest_framework.viewsets import ModelViewSet
from .models import Shop
from .serializers import ShopImportSerializer, ShopStateSerializer, ShopOrderSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orders.models import Order


class ShopImportViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopImportSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']


class ShopStateViewSet(ModelViewSet):
    serializer_class = ShopStateSerializer
    permission_classes = [IsAuthenticated]
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
    serializer_class = ShopOrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self):
        # return Order.objects.prefetch_related('products').filter(products__shop__in=shops).distinct()
        # shops = Shop.objects.filter(user=self.request.user)
        # pis = ProductInfo.objects.select_related('shop').filter(shop__in=shops)
        # return Order.objects.filter(products__in=pis)
        # Order.objects.prefetch_related('products__shop') <- best one for just orders
        # return Shop.objects.filter(user=self.request.user)
        # Order.objects.prefetch_related('products__shop').filter(products__shop__in=shops)
        # shops = Shop.objects.filter(user=self.request.user)
        return Shop.objects.only('id', 'name')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        print(f'queryset: {queryset}')
        if not queryset:
            return Response({'results': 'There is no orders associated with shops you manage.'})

        serializer = self.get_serializer(queryset, many=True)
        print(f'serializer.data: {serializer.data}')
        return Response(serializer.data)

