from distutils.util import strtobool

from django.db import IntegrityError
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import URLValidator
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from ujson import loads as load_json

from backend.models import Category, Shop, ProductInfo, ConfirmEmailToken, Contact, OrderItem, Order, STATE_CHOICES
from backend.permissions import IsShopUser, IsCustomAdminUser
from backend.serializers import UserSerializer, ContactSerializer, ShopSerializer, CategorySerializer, \
    ProductInfoSerializer, OrderSerializer, OrderItemSerializer
from backend.signals import new_user_registered, new_order, update_order

from backend.tasks import do_import


class RegisterAccount(APIView):

    def post(self, request, *args, **kwargs):

        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                errors = []
                # noinspection PyTypeChecker
                for item in password_error:
                    errors.append(item)
                return JsonResponse(
                    {'Status': False, 'Errors': {'password': errors}},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    try:
                        new_user_registered.send(sender=self.__class__, user_id=user.id)
                    except Exception as err:
                        return JsonResponse(
                            {'Status': False, 'Errors': err.__str__()},
                            status=status.HTTP_400_BAD_REQUEST)

                    return JsonResponse({'Status': 'OK'}, status=status.HTTP_201_CREATED)
                else:
                    return JsonResponse(
                        {'Status': False, 'Errors': user_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        return JsonResponse(
            {'Status': False, 'Errors': 'Arguments not found'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ConfirmAccount(APIView):

    def post(self, request, *args, **kwargs):

        if {'token', 'email'}.issubset(request.data):

            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()

            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return JsonResponse({'Status': 'OK'}, status=status.HTTP_200_OK)

            return JsonResponse(
                {'Status': False, 'Error': 'Email и/или token не правильный'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'Status': False, 'Error': 'Не переданы необходимые поля'},
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginAccount(APIView):

    def post(self, request, *args, **kwargs):

        if {'email', 'password'}.issubset(request.data):

            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)

                    return JsonResponse(
                        {'Status': 'OK', 'Token': token.key},
                        status=status.HTTP_200_OK
                    )

                return JsonResponse(
                    {'Status': False, 'Error': 'Подтвердите почту'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return JsonResponse(
                {'Status': False, 'Error': 'Не удается войти'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'Status': False, 'Error': 'Не переданы обязательные поля'},
            status=status.HTTP_400_BAD_REQUEST
        )


class AccountDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user_serializer = UserSerializer(request.user)
        return JsonResponse(user_serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        if 'password' in request.data:

            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse(
                    {'Status': False, 'Errors': {'password': error_array}},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                request.user.set_password(request.data['password'])

        user_serializer = UserSerializer(request.user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse(user_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(
                {'Status': False, 'Errors': user_serializer.errors},
                status.HTTP_400_BAD_REQUEST
            )


class Logout(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        request.user.auth_token.delete()
        return JsonResponse({'LogoutStatus': 'OK'}, status=status.HTTP_204_NO_CONTENT)


class ContactView(APIView):
    """
    Класс для работы с контактами покупателей
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        contact = Contact.objects.filter(
            user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        if {'city', 'street', 'phone'}.issubset(request.data):
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse(
                    {'Status': False, 'Errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return JsonResponse(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST
        )

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
                return JsonResponse(
                    {'Status': True, 'Удалено объектов': deleted_count},
                    status=status.HTTP_200_OK
                )
        return JsonResponse(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, *args, **kwargs):
        if 'id' in request.data:
            if type(request.data['id']) == str and request.data['id'].isdigit():
                contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first()
                if contact:
                    serializer = ContactSerializer(contact, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse({'Status': True}, status=status.HTTP_200_OK)
                    else:
                        return JsonResponse(
                            {'Status': False, 'Errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST
                        )

            return JsonResponse(
                {'State': False, 'Error': 'Неверный тип данных'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST
        )


class PartnerState(APIView):
    permission_classes = (IsAuthenticated, IsShopUser)

    def get(self, request, *args, **kwargs):

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(state=strtobool(state))
                return JsonResponse({'Status': True}, status=status.HTTP_201_CREATED)
            except ValueError as error:
                return JsonResponse(
                    {'Status': False, 'Errors': str(error)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return JsonResponse(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST
        )


class PartnerOrders(APIView):
    permission_classes = (IsAuthenticated, IsShopUser)

    def get(self, request, *args, **kwargs):
        order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """
    permission_classes = (IsAuthenticated, IsShopUser)

    def post(self, request, *args, **kwargs):

        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse(
                    {'Status': False, 'Error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                info = do_import(url=url, user_id=request.user.id)
                return JsonResponse({'Status': info}, status=status.HTTP_201_CREATED)

        return JsonResponse(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, *args, **kwargs):
        if {'id'}.issubset(request.data) and type(request.data['id']) == int:
            product = ProductInfo.objects.filter(
                shop__user_id=request.user.id,
                external_id=request.data['id']
            ).first()
            if product:
                serializer = ProductInfoSerializer(product, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse({'Status': True}, status=status.HTTP_200_OK)

                return JsonResponse({**serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse(
                {'Status': False, 'Error': f'Продукта с id:{request.data["id"]} нету в вашем магазине'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return JsonResponse(
            {'Status': False, 'Error': 'Не указанный необходимые поля'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, *args, **kwargs):

        items_sting = request.data.get('items')

        if items_sting:
            items_list = items_sting.split(',')
            query = Q()
            objects_deleted = False
            for product_item_id in items_list:
                if product_item_id.isdigit():
                    query = query | Q(shop__user_id=request.user.id, external_id=product_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_info = ProductInfo.objects.filter(query).delete()
                deleted_count = deleted_info[1].get('backend.ProductInfo', 0)
                return JsonResponse(
                    {'Status': True, 'Удалено объектов': deleted_count},
                    status=status.HTTP_200_OK
                )
        return JsonResponse(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ShopsView(ListAPIView):
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductInfoView(APIView):

    def get(self, request, *args, **kwargs):

        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        queryset = ProductInfo.objects.filter(
            query).select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()

        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class BasketView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):

        basket = Order.objects.filter(
            user_id=request.user.id, state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                return JsonResponse(
                    {'Status': False, 'Errors': 'Неверный формат запроса'},
                    status=status.HTTP_400_BAD_REQUEST
                )
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
                            return JsonResponse(
                                {'Status': False, 'Errors': str(error)},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        else:
                            objects_created += 1

                    else:

                        return JsonResponse(
                            {'Status': False, 'Errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                return JsonResponse(
                    {'Status': True, 'Создано объектов': objects_created},
                    status=status.HTTP_201_CREATED
                )
        return JsonResponse(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, *args, **kwargs):

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
                return JsonResponse(
                    {'Status': True, 'Удалено объектов': deleted_count},
                    status=status.HTTP_200_OK
                )
        return JsonResponse(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, *args, **kwargs):

        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                return JsonResponse(
                    {'Status': False, 'Errors': 'Неверный формат запроса'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_updated = 0
                for order_item in items_dict:
                    if type(order_item['id']) == int and type(order_item['quantity']) == int:
                        objects_updated += OrderItem.objects.filter(order_id=basket.id, id=order_item['id']).update(
                            quantity=order_item['quantity'])

                return JsonResponse(
                    {'Status': True, 'Обновлено объектов': objects_updated},
                    status=status.HTTP_200_OK
                )
        return JsonResponse(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST
        )


class OrderView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None, *args, **kwargs):
        if pk is not None:
            order = Order.objects.filter(
                user_id=request.user.id).filter(id=int(pk)).exclude(state='basket').prefetch_related(
                'ordered_items__product_info__product__category',
                'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
                total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
            if not order:
                return JsonResponse(
                    {'Error': f'У вас нету заказа №:{pk}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = OrderSerializer(order, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        order = Order.objects.filter(
            user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        if {'id', 'contact'}.issubset(request.data):
            if request.data['id'].isdigit() and request.data['contact'].isdigit():
                try:
                    is_updated = Order.objects.filter(
                        user_id=request.user.id, id=request.data['id']).update(
                        contact_id=request.data['contact'],
                        state='new'
                    )
                except IntegrityError as error:
                    return JsonResponse(
                        {'Status': False, 'Errors': f'{error}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    if is_updated:
                        new_order.send(sender=self.__class__,
                                       user_id=request.user.id)
                        return JsonResponse(
                            {'Status': True},
                            status=status.HTTP_201_CREATED
                        )

        return JsonResponse(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST
        )


class AdminView(APIView):
    permission_classes = (IsCustomAdminUser,)

    def put(self, request, *args, **kwargs):

        if {'id', 'state'}.issubset(request.data):
            dict_state = dict(STATE_CHOICES)
            if request.data['state'] not in dict_state.keys():
                return JsonResponse(
                    {'Error': 'Неверный статус'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                Order.objects.filter(id=request.data['id']).update(state=request.data['state'])
            except IntegrityError as error:
                return JsonResponse(
                    {'Error': error},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order_info = Order.objects.get(id=request.data['id'])
            update_order.send(
                sender=self.__class__,
                user_id=order_info.user_id,
                order_id=order_info.id,
                state=dict_state[request.data['state']]
            )
            return JsonResponse(
                {"Status": True},
                status=status.HTTP_200_OK
            )

        return JsonResponse(
            {'Error': 'Указанны не все поля'},
            status=status.HTTP_400_BAD_REQUEST
        )
