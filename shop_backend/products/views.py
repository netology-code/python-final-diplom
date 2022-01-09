from rest_framework.viewsets import ModelViewSet
from .models import ProductInfo
from .serializers import ProductSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ShopCategoryFilter


class ProductInfoViewSet(ModelViewSet):
    queryset = ProductInfo.objects.prefetch_related('shop', 'product')
    serializer_class = ProductSerializer
    lookup_field = 'product__id'
    filter_backends = [DjangoFilterBackend]
    filter_class = ShopCategoryFilter
    http_method_names = ['get']
