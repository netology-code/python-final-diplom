from rest_framework.viewsets import ModelViewSet
from .models import Product
from .serializers import ProductSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductShopCategoryFilter


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.filter(shops__is_closed=False).distinct('name')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = ProductShopCategoryFilter
    http_method_names = ['get']
