from rest_framework.viewsets import ModelViewSet
from .models import Shop
from .serializers import ShopImportSerializer, ShopStateSerializer, ShopOrderSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orders.serializers import OrderItemsSerializer
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
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self):
        shops = Shop.objects.filter(user=self.request.user)
        if self.kwargs.get('pk'):
            return Order.objects.filter(shop__in=shops)

        return shops

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({'results': 'There is no orders associated with shops you manage.'})

        serializer = ShopOrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        print(f'instance: {instance}')
        serializer = OrderItemsSerializer(instance)
        print(f'serializer: {serializer}')
        return Response(serializer.data)
