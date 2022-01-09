from rest_framework.viewsets import ModelViewSet
from .models import Product
from .serializers import ProductSerializer


# from django_filters.rest_framework import DjangoFilterBackend
# from .filters import ShopCategoryFilter


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('shops')
    serializer_class = ProductSerializer
    lookup_field = 'product__id'
    # filter_backends = [DjangoFilterBackend]
    # filter_class = ShopCategoryFilter
    http_method_names = ['get']
