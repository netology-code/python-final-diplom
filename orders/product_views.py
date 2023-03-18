from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from orders.models import Product, Shop, ProductInfo, Parameter, \
    ProductParameter, Category
from django.core.validators import URLValidator
from django.db.models import Q
from django.http import JsonResponse
from requests import get

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from rest_framework.views import APIView

from yaml import Loader, load as load_yaml

from pprint import pprint
from orders.serializers import ProductSerializer, ShopSerializer, ProductViewSerializer, \
    SingleProductViewSerializer, CategorySerializer


class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """

    def post(self, request, *args, **kwargs):

        # если пользователь не авторизован
        if not request.user.is_authenticated:
            print('пользователь не авторизован')
            return JsonResponse({'Status': False, 'Error': 'Login required'}, status=403)

        # если тип пользователя не "магазин"
        if request.user.user_type != 'shop':
            print('тип пользователя не "магазин"')
            return JsonResponse(
                {'Status': False, 'Error': 'Только для магазинов'},
                status=403)

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
                    category_object, _ = Category.objects.get_or_create(
                        id=category['id'],
                        name=category['name'])
                    category_object.shops.add(shop.id)
                    category_object.save()

                # Обработка данных товара
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:

                    # Продукт
                    product, _ = Product.objects.get_or_create(
                        name=item['name'],
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
        return JsonResponse(
            {'Status': False,
             'Errors': 'Не указаны все необходимые аргументы'})


class ProductsList(ListAPIView):
    """
    Список товаров
    """
    queryset = Product.objects.filter(product_info__shop__state=True)
    serializer_class = ProductSerializer


class ProductDetailAPIView(APIView):

    def get(self, request, *args, **kwargs):
        print(f"self.request: {self.request.query_params.get('shop_id')}")
        return Response(status=status.HTTP_200_OK)


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

    permission_classes = [AllowAny]

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
