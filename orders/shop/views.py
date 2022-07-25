import json

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from ujson import loads as load_json
from django.db.models.query import Prefetch

from orders import settings
from .models import Shop, Category, ProductInfo, Order, OrderItem
from .permissions import IsOnlyShop
from .serializers import UserSerializer, ShopSerializer, CategorySerializer, ProductInfoSerializer, OrderSerializer, \
    OrderItemSerializer, ContactSerializer
from custom_auth.models import ConfirmEmailToken, Contact
from .signals import new_user_registered
from .tasks import import_shop_data


class RegisterAccount(APIView):
    """Регистрация покупателей"""

    def post(self, request, *args, **kwargs):
        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):
            errors = {}
            # проверяем пароль на сложность
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                # Проверяем уникальность имени пользователя
                # request.data._mutable = True
                request.data.update({})
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    # Сохраняем пользователя
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    new_user_registered.send(sender=__class__, user_id=user.id)
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ConfirmAccount(APIView):
    """Класс для подтверждения электронного адреса"""

    def post(self, request, *args, **kwargs):
        # Проверяем обязательные аргументы
        if {'email', 'token'}.issubset(request.data):
            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return Response({'Status': True})
            else:
                return Response({'Status': False, 'Errors': 'Неправильно указан токен или email'})
        return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'},
                        status=status.HTTP_400_BAD_REQUEST)


class LoginAccount(APIView):
    """Класс для авторизации пользователя"""

    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({'Status': True, 'Token': token.key})

            return Response({'Status': False, 'Errors': 'Не удалось авторизоваться'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'},
                        status=status.HTTP_400_BAD_REQUEST)


class AccountDetails(APIView):
    """Класс для работы с данными пользователя"""
    permission_classes = [IsAuthenticated]

    # Возвращаем все данные пользователя + все контакты
    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    # Изменяем данные пользователя
    def post(self, request, *args, **kwargs):
        # Если пароль есть, проверяем его
        if 'password' in request.data:
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                return Response({'Status': False, 'Errors': {'password': password_error}})
            else:
                request.user.set_password(request.data['password'])

        # Проверяем остальные данные
        user_serializer = UserSerializer(request.user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({'Status': True}, status=status.HTTP_201_CREATED)
        else:
            return Response({'Status': False, 'Errors': user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CategoryView(ModelViewSet):
    """ Класс для просмотра категорий """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    ordering = ('name',)


class ShopView(ModelViewSet):
    """ Класс для просмотра магазинов """

    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    ordering = ('name',)


class ProductInfoView(ReadOnlyModelViewSet):
    """ Класс для поиска товаров """

    serializer_class = ProductInfoSerializer
    ordering = ('product',)

    def get_queryset(self):

        query = Q(shop__state=True)
        shop_id = self.request.query_params.get('shop_id')
        category_id = self.request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(category_id=category_id)

        # Фильтруем и отбрасываем дубликаты
        queryset = ProductInfo.objects.filter(query) \
            .select_related('shop', 'product__category') \
            .prefetch_related('product_parameters__parameter') \
            .distinct()

        return queryset


class BasketView(APIView):
    """ Класс для работы с корзиной пользователя """
    permission_classes = [IsAuthenticated]

    # Получаем корзину
    def get(self, request, *args, **kwargs):

        basket = Order.objects.filter(user_id=request.user.id, status='basket') \
            .prefetch_related('ordered_items__product_info__product__category',
                              'ordered_items__product_info__product_parameters__parameter') \
            .annotate(total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))) \
            .distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    # Редактируем корзину
    def post(self, request, *args, **kwargs):

        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = json.dumps(items_sting)
            except ValueError:
                JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='basket')
                objects_created = 0
                for order_item in load_json(items_dict):
                    order_item.update({'order': basket.id})
                    serializer = OrderItemSerializer(data=order_item)
                    if serializer.is_valid(raise_exception=True):
                        try:
                            serializer.save()
                        except IntegrityError as error:
                            return JsonResponse({'Status': False, 'Errors': str(error)})
                        else:
                            objects_created += 1
                    else:
                        JsonResponse({'Status': False, 'Errors': serializer.errors})

                return JsonResponse({'Status': True, 'Создано объектов': objects_created})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все обязательные аргументы'})

    # Удаление позиции из корзины
    def delete(self, request, *args, **kwargs):

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='basket')
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order_id=basket.id, id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                delete_count = OrderItem.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': delete_count})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все обязательные аргументы'})

    # Добавляем позицию в корзину
    def put(self, request, *args, **kwargs):

        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = json.dumps(items_sting)
            except ValueError:
                JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='basket')
                objects_update = 0
                for order_item in json.loads(items_dict):
                    if type(order_item['id']) == int and type(order_item['quantity']) == int:
                        objects_update += OrderItem.objects.filter(order_id=basket.id, id=order_item['id']) \
                            .update(quantity=order_item['quantity'])

                return JsonResponse({'Status': True, 'Обновлено объектов': objects_update})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все обязательные аргументы'})


class OrderView(APIView):
    """ Класс для получения и размещения заказов пользователями """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        order = Order.objects.filter(user_id=request.user.id) \
            .exclude(status='basket') \
            .select_related('contact') \
            .prefetch_related('ordered_items') \
            .annotate(total_quantity=Sum('ordered_items__quantity'), total_sum=Sum('ordered_items__total_amount')) \
            .distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    # Размещение заказа из корзины и отправка письма об изменении статуса заказа.
    def post(self, request, *args, **kwargs):

        if request.data['id'].isdigit():
            try:
                is_update = Order.objects.filter(id=request.data['id'], user_id=request.user.id) \
                    .update(contact_id=request.data['contact'], status='new')
            except IntegrityError as error:
                return Response({'Status': False, 'Errors': error},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                if is_update:
                    request.user.email_user(f'Обновление статуса заказа', 'Заказ сформирован',
                                            from_email=settings.EMAIL_HOST_USER)
                    return Response({'Status': True})

        return Response({'Status': False, 'Errors': 'Не указаны все обязательные аргументы'},
                        status=status.HTTP_400_BAD_REQUEST)


class ContactView(APIView):
    """ Класс для работы с контактами покупателей """
    permission_classes = [IsAuthenticated]

    # Показать свои контакты
    def get(self, request, *args, **kwargs):

        contact = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    # Добавляем новый контакт
    def post(self, request, *args, **kwargs):

        if {'city', 'phone'}.issubset(request.data):
            request.data._mutable = True
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все обязательные аргументы'})

    # Удаляем контакт
    def delete(self, request, *args, **kwargs):

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            query = Q()
            objects_deleted = False
            for contact_id in items_list:
                if contact_id.isdigit():
                    query = query | Q(user_id=request.user.id, id=contact_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = Contact.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все обязательные аргументы'})

    # Редактируем контакт
    def put(self, request, *args, **kwargs):

        if 'id' in request.data:
            if request.data['id'].isdigit():
                contact = Contact.objects.filter(id=request.data['id'], user_id=request.data.id).first()
                print(contact)
                if contact:
                    serializer = ContactSerializer(contact, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse({'Status': True})
                    else:
                        JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все обязательные аргументы'})


class PartnerOrders(APIView):
    """ Класс для получения заказов поставщиками """
    permission_classes = [IsAuthenticated, IsOnlyShop]

    def get(self, request, *args, **kwargs):
        order = Order.objects.filter(user_id=request.user.id) \
            .exclude(status='basket') \
            .prefetch_related('ordered_items__product_info__product__category',
                              'ordered_items__product_info__product_parameters__parameter') \
            .select_related('contact') \
            .annotate(total_sum=Sum('ordered_items__total_amount', total_quantity=Sum('ordered_items__quantity')))

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)


class PartnerState(APIView):
    """ Класс для работы со статусом поставщика """
    permission_classes = [IsAuthenticated, IsOnlyShop]

    # Получаем текущий статус получения заказов у магазина
    def get(self, request, *args, **kwargs):
        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    # Изменяем текущий статус получения заказа у магазина
    def post(self, request, *args, **kwargs):
        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(state=eval(state))
                return Response({'Status': True})
            except ValueError as error:
                return Response({'Status': False, 'Errors': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'Status': False, 'Errors': 'Не указан аргумент state'}, status=status.HTTP_400_BAD_REQUEST)


class PartnerUpdate(APIView):
    """ Класс для обновления прайса от поставщика """
    permission_classes = [IsAuthenticated, IsOnlyShop]

    def post(self, request, *args, **kwargs):
        url = request.data.get('url')
        if url:
            try:
                import_shop_data.delay(request.user.id, url)
            except IntegrityError as e:
                return JsonResponse({'Status': False, 'Errors': f'Integrity Error: {e}'})

            return Response({'Status': True}, status=status.HTTP_200_OK)

        return Response({'Status': False, 'Errors': 'Не указаны все обязательные аргументы'},
                        status=status.HTTP_400_BAD_REQUEST)
