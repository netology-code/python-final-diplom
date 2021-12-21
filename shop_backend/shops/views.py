from rest_framework.response import Response

from shops.models import Shop
from rest_framework.viewsets import ModelViewSet
from .serializers import ShopSerializer


class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    http_method_names = ['post']
