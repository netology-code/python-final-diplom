from sqlite3 import IntegrityError

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from orders.models import Product, Shop, ProductInfo, Parameter, \
    ProductParameter, Category, Order, OrderItem
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import URLValidator
from django.db.models import Q, F, Sum
from django.http import JsonResponse
from requests import get

from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from rest_framework.views import APIView

from yaml import Loader, load as load_yaml
from ujson import loads as load_json

from pprint import pprint
from orders.serializers import UserSerializer, ProductSerializer, ShopSerializer, ProductViewSerializer, \
    SingleProductViewSerializer, CategorySerializer, OrderSerializer, OrderItemSerializer


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


class CategoryView(ListAPIView):
    """
    Список категорий
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """

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


class SingleProductView(APIView):
    """
    Поиск товаров по product_id
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        print(f'product_id: {product_id}')

        queryset = ProductInfo.objects.filter(product__id=product_id)

        serializer = SingleProductViewSerializer(queryset, many=True)

        return Response(serializer.data)


class ProductInfoViewSet(APIView):
    """
    Класс для поиска товаров
    по:
    product_id
    shop_id
    category_id
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SingleProductViewSerializer,
        responses={200: SingleProductViewSerializer},
    )
    def get(self, request, *args, **kwargs):
        """
        Метод get_queryset принимает критерии для поиска,
        возвращает товары, в соотвествии с запросом. """

        query = Q(shop__state=True)
        product_id = request.data.get('product_id')
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if product_id:
            query = query & Q(product__id=product_id)

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        print(f'query: {query}')

        queryset = ProductInfo.objects.filter(
            query).select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()

        serializer = SingleProductViewSerializer(queryset, many=True)

        return Response(serializer.data)


class BasketView(APIView):
    """
    Класс для работы с корзиной пользователя
    """

    # получить корзину
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        basket = Order.objects.filter(
            user_id=request.user.id, state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    # редактировать корзину
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_created = 0
                for order_item in items_dict:
                    order_item.update({'order': basket.id})
                    serializer = OrderItemSerializer(data=order_item)
                    if serializer.is_valid():
                        try:
                            serializer.save()
                        except IntegrityError as error:
                            return JsonResponse({'Status': False, 'Errors': str(error)})
                        else:
                            objects_created += 1

                    else:

                        JsonResponse({'Status': False, 'Errors': serializer.errors})

                return JsonResponse({'Status': True, 'Создано объектов': objects_created})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # удалить товары из корзины
    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order_id=basket.id, id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # добавить позиции в корзину
    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_updated = 0
                for order_item in items_dict:
                    if type(order_item['id']) == int and type(order_item['quantity']) == int:
                        objects_updated += OrderItem.objects.filter(order_id=basket.id, id=order_item['id']).update(
                            quantity=order_item['quantity'])

                return JsonResponse({'Status': True, 'Обновлено объектов': objects_updated})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
