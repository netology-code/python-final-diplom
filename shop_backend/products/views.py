from rest_framework.viewsets import ModelViewSet
from .models import ProductInfo
from .serializers import ProductInfoSerializer


class ProductInfoViewSet(ModelViewSet):
    queryset = ProductInfo.objects.prefetch_related('shop', 'product')
    serializer_class = ProductInfoSerializer
    lookup_field = 'product__id'
    http_method_names = ['get']
