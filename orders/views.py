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

from pprint import pprint


# , Order, OrderItem, \
# ConfirmEmailToken, Contact, User

class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """
    def post(self, request, *args, **kwargs):

        print(f'request: {request} \nargs: {args}\nkwargs: {kwargs}')
        print(f'request.user: {request.user}')

        # если пользователь не авторизован
        if not request.user.is_authenticated:
            print('пользователь не авторизован')
            return JsonResponse({'Status': False, 'Error': 'Login required'}, status=403)

        # если тип пользователя не "магазин"
        if request.user.user_type != 'shop':
            print('тип пользователя не "магазин"')
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        url = request.data.get('url')
        print(f'url: {url}')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                print('ValidationError')
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                stream = get(url).content

                data = load_yaml(stream, Loader=Loader)
                print('data:')
                pprint(data)

                shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
                    category_object.shops.add(shop.id)
                    category_object.save()
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

                    product_info = ProductInfo.objects.create(product_id=product.id,
                                                              external_id=item['id'],
                                                              model=item['model'],
                                                              price=item['price'],
                                                              price_rrc=item['price_rrc'],
                                                              quantity=item['quantity'],
                                                              shop_id=shop.id)
                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_info_id=product_info.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value)

                return JsonResponse({'Status': True})

        print('Не указаны все необходимые аргументы')
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
