from rest_framework.viewsets import ModelViewSet
from .models import Product
from .serializers import ProductSerializer, ProductDetailsSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductShopCategoryFilter
from rest_framework.response import Response


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.filter(shops__is_closed=False).distinct('name')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = ProductShopCategoryFilter
    http_method_names = ['get']

    def retrieve(self, request, *args, **kwargs):
        instance = super().get_object()
        serializer = ProductDetailsSerializer(instance)
        return Response(serializer.data)
