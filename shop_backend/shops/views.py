from rest_framework import serializers
from rest_framework.response import Response

from shops.models import Shop
from rest_framework.viewsets import ModelViewSet
from .serializers import ShopSerializer


class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    http_method_names = ['post']

    # class Meta:
    #     model = Shop
    #     fields = ['filename', 'url']
    #
    # def create(self, request, *args, **kwargs):
    #     return Response({'jopa': 'tolstaya'})
    #
    # def validate(self, data):
    #     price_list_filename = data.get('filename')
    #     price_list_url = data.get('url')
    #
    #     if not (price_list_filename or price_list_url):
    #         pass

        #return data
