# from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView

from orders.models import Product, Shop, ProductInfo, Parameter, \
    ProductParameter, Category  # , ConfirmEmailToken
# from distutils.util import strtobool
#
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import URLValidator
# from django.db import IntegrityError
# from django.db.models import Q, Sum, F
from django.http import JsonResponse
from requests import get

from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
# from rest_framework.generics import ListAPIView
# from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

# from rest_framework.viewsets import ModelViewSet


from rest_framework.views import APIView

from yaml import Loader, load as load_yaml

from pprint import pprint

# , Order, OrderItem, \
# ConfirmEmailToken, Contact, User
# from orders.serializers import UserSerializer
# orders.signals import new_user_registered
from orders.serializers import UserSerializer, ProductSerializer, ShopSerializer, ProductViewSerializer, \
    SingleProductViewSerializer


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

                # Обработка данных магазина
                shop, _ = Shop.objects.get_or_create(name=data['shop'],
                                                     user_id=request.user.id)

                # Обработка категории товара
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(id=category['id'],
                                                                        name=category['name'])
                    category_object.shops.add(shop.id)
                    category_object.save()

                # Обработка данных товара
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:

                    # Продукт
                    product, _ = Product.objects.get_or_create(name=item['name'],
                                                               category_id=item['category'])
                    # Данные продукта
                    product_info = ProductInfo.objects.create(product_id=product.id,
                                                              external_id=item['id'],
                                                              model=item['model'],
                                                              price=item['price'],
                                                              price_rrc=item['price_rrc'],
                                                              quantity=item['quantity'],
                                                              shop_id=shop.id)
                    for name, value in item['parameters'].items():
                        # Параметры продукта
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_info_id=product_info.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value)

                return JsonResponse({'Status': True})

        print('Не указаны все необходимые аргументы')
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class LoginAccount(APIView):
    """
    Класс для авторизации пользователей
    """

    # Авторизация методом POST
    def post(self, request, *args, **kwargs):

        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)

                    return JsonResponse({'Status': True, 'Token': token.key})

            return JsonResponse({'Status': False, 'Errors': 'Не удалось авторизовать'})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class RegisterAccount(APIView):
    """
    Для регистрации покупателей
    """

    # Регистрация методом POST
    def post(self, request, *args, **kwargs):

        # проверяем обязательные аргументы
        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):

            # проверяем пароль на сложность

            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                # проверяем данные для уникальности имени пользователя
                request.data._mutable = True
                request.data.update({})
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    # сохраняем пользователя
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ProductsList(ListAPIView):
    """
    Список товаров
    """
    queryset = Product.objects.filter(product_info__shop__state=True)
    serializer_class = ProductSerializer


class SingleProductView(APIView):

    def get(self, request):
        product_id = request.data.get('product_id')
        print(f'product_id: {product_id}')

        products = Product.objects.filter(product_id=product_id)

        serializer = SingleProductViewSerializer(products, many=True)
        return Response(serializer.data)


class ShopView(ListAPIView):
    """ Класс для просмотра списка магазинов """

    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class ProductsView(APIView):
    def get(self, request):

        category = request.data.get('category')
        shop = request.data.get('shop')
        print(f'category: {category}')
        print(f'shop: {shop}')

        products = Product.objects.filter(product_info__shop__name=shop,
                                          category__name=category)

        serializer = ProductViewSerializer(products, many=True)
        return Response(serializer.data)
