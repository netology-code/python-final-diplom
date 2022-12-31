from orders.models import Product, Shop, ProductInfo, Parameter, ProductParameter, Category
# from distutils.util import strtobool
#
# from django.contrib.auth import authenticate
# from django.contrib.auth.password_validation import validate_password
from django.core.validators import URLValidator
# from django.db import IntegrityError
# from django.db.models import Q, Sum, F
from django.http import JsonResponse
from requests import get

# from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
# from rest_framework.generics import ListAPIView
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.response import Response

# from rest_framework.viewsets import ModelViewSet


from rest_framework.views import APIView

from yaml import Loader, load as load_yaml


# , Order, OrderItem, \
# ConfirmEmailToken, Contact, User

class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """
    throttle_scope = 'price-list'

    def post(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return JsonResponse({'Status': 403,
                                 'Error': 'Только для магазинов'})

        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': 404, 'Error': str(e)})
            else:
                stream = get(url).content

                data = load_yaml(stream, Loader=Loader)

                shop, _ = Shop.objects.get_or_create(name=data['shop'])
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(
                        id=category['id'],
                        name=category['name'])
                    category_object.shops.add(shop.id)
                    category_object.save()
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(
                        name=item['name'], category_id=item['category'])

                    product_info = ProductInfo.objects.create(
                        product_id=product.id,
                        name=item['model'],
                        price=item['price'],
                        price_rrc=item['price_rrc'],
                        quantity=item['quantity'],
                        shop_id=shop.id)
                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(
                            name=name)
                        ProductParameter.objects.create(
                            product_info_id=product_info.id,
                            parameter_id=parameter_object.id,
                            value=value)

                return JsonResponse({'Status': 200, 'Message': 'Success'})

        return JsonResponse({'Status': 411,
                             'Errors': 'Не указаны все необходимые аргументы'})
