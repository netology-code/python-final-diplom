from distutils.util import strtobool

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.db.models import F, Q, Sum
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.openapi import Parameter as yasg_param, IN_PATH
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ujson import loads as load_json

from backend.models import STATE_CHOICES, Category, ConfirmEmailToken, Contact, Order, OrderItem, ProductInfo, Shop, \
    USER_TYPE_CHOICES
from backend.permissions import IsCustomAdminUser, IsShopUser
from backend.serializers import (CategorySerializer, ContactSerializer, OrderItemSerializer, OrderSerializer,
                                 ProductInfoSerializer, ShopSerializer, UserSerializer, ImageSerializers)
from backend.signals import new_order, new_user_registered, update_order
from backend.tasks import do_import, delete_image


class RegisterAccount(APIView):
    """
    Class for registering new users
    """

    @swagger_auto_schema(
        operation_summary='Register users',
        operation_description='Register a new user account',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.FORMAT_EMAIL, description='user email'),
                "password": openapi.Schema(type=openapi.FORMAT_PASSWORD, description="password"),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='str first name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='str last name'),
                'company': openapi.Schema(type=openapi.TYPE_STRING, description='str company'),
                'position': openapi.Schema(type=openapi.TYPE_STRING, description='str position in the company'),
                "type": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=[type[0] for type in USER_TYPE_CHOICES],
                )
            },
            required=['email', 'password', 'first_name', 'last_name', 'company', 'position']),
        responses={201: "OK", 400: False}
    )
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
    """
    Class for confirming the user's mail
    """

    @swagger_auto_schema(
        operation_summary='Confirm email',
        operation_description='Confirm registered email of user',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.FORMAT_EMAIL, description='user email'),
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='token from email'),

            },
            required=['email', 'token'])
    )
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
    """
    Class for user authorization
    """

    @swagger_auto_schema(
        operation_summary='Login account',
        operation_description='Login in the app',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.FORMAT_EMAIL, description='confirm email'),
                'password': openapi.Schema(type=openapi.FORMAT_PASSWORD, description='users password'),
            },
            required=['email', 'password']
        ), responses={200: "OK",
                      400: False}
    )
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
    """
    Class for viewing and editing information
    in the user account:
    :get: Receiving information about the user's account.
    :post: Updating user's account information.
    """

    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_summary='Account info',
        operation_description='Viewing the user profile',
        responses={200: openapi.Response(description='Профиль пользователя',
                                         schema=UserSerializer(read_only=True))})
    def get(self, request, *args, **kwargs):
        user_serializer = UserSerializer(request.user)
        return JsonResponse(user_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Update account info',
        operation_description='Changing account info',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'password': openapi.Schema(type=openapi.FORMAT_PASSWORD, description='users password'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='str first name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='str last name'),
                'company': openapi.Schema(type=openapi.TYPE_STRING, description='str company'),
                'position': openapi.Schema(type=openapi.TYPE_STRING, description='str position in the company'),
            },
        ), responses={200: "OK",
                      400: False}
    )
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
    """
    Class fot Logout the app.
    """
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_summary='Logout the app',
        operation_description='Logout user from the app',
        responses={200: "OK"},
    )
    def get(self, request):
        request.user.auth_token.delete()
        return JsonResponse({'LogoutStatus': 'OK'}, status=status.HTTP_204_NO_CONTENT)


class ContactView(APIView):
    """
    Class for working with user contacts:
    :get: Receiving the user's contacts list.
    :post: Create a new contact for the user.
    :put: Change the user's contact by several fields.
    :delete: Delete one contact or more contacts of the user.
    """
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_summary='Contact info',
        operation_description='Viewing the user contact',
        responses={200: openapi.Response(description='User contact',
                                         schema=ContactSerializer(read_only=True))}
    )
    def get(self, request, *args, **kwargs):

        contact = Contact.objects.filter(
            user_id=request.user.id
        )
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Create contact',
        operation_description='Creating a contact of user',
        request_body=ContactSerializer,
        responses={201: 'True',
                   400: False}
    )
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

    @swagger_auto_schema(
        operation_summary='Delete contact',
        operation_description='Deleting the contact or multiple contacts',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'items': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='A comma-separated ids list of the user contacts'
                )
            },
            required=['items'],
        ),
        responses={200: 'True',
                   400: False}
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

    @swagger_auto_schema(
        operation_summary='Change contact',
        operation_description='Changing the user contact by several fields',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User contact id'
                )
            },
            required=['id'],
        ),
        responses={200: 'True',
                   400: False}
    )
    def put(self, request, *args, **kwargs):
        if 'id' in request.data:
            if type(request.data['id']) is str and request.data['id'].isdigit():
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
    """
    Class for viewing and changing the status of the store:
    :get: Receiving info about status of shop.
    :post: Change shop status between True or False.
    """

    permission_classes = (IsAuthenticated, IsShopUser)

    @swagger_auto_schema(
        operation_summary='Shop status info',
        operation_description='Viewing the shop status',
        responses={200: openapi.Response(description='Status',
                                         schema=ShopSerializer(read_only=True))}
    )
    def get(self, request, *args, **kwargs):

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Change status',
        operation_description='Changing the shop status',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'state': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=[True, False],
                )
            },
            required=['state']
        ),
        responses={200: openapi.Response(description='Status',
                                         schema=ShopSerializer(read_only=True))}
    )
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
    """
    Class for receiving shop orders
    """
    permission_classes = (IsAuthenticated, IsShopUser)

    @swagger_auto_schema(
        operation_summary='Shop orders',
        operation_description='Viewing the shop orders',
        responses={200: openapi.Response(description='Orders',
                                         schema=OrderSerializer(many=True),
                                         total_sum=openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                  description='Total order price')
                                         )
                   }
    )
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
    Class for adding, changing and deleting
    a price list from a supplier:
    :post: Creating or updating a supplier's price list using the url.
    :put: Changing product info according to the specified parameters.
    :delete: Removing the product from the store's price list.
    """
    permission_classes = (IsAuthenticated, IsShopUser)

    @swagger_auto_schema(
        operation_summary='Update price',
        operation_description='Updating te shop price',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'url': openapi.Schema(
                    type=openapi.FORMAT_URI,
                    description='The url must have data about the stores price list in yml format'
                )
            },
            required=['url']
        ),
        responses={201: 'True',
                   400: False}
    )
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

    @swagger_auto_schema(
        operation_summary='Change shop product',
        operation_description='Changing product info according to the specified parameters',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='The external id of the product info that need to be changed'
                ),
                'quantity': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Positive number'
                ),
                'price': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Positive number'
                ),
                'price_rcc': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Positive number'
                ),
                'model': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Model name'
                )
            },
            required=['id']
        ),
        responses={200: 'True',
                   400: False}
    )
    def put(self, request, *args, **kwargs):
        if {'id'}.issubset(request.data) and type(request.data['id']) is int:
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

    @swagger_auto_schema(
        operation_summary='Delete product of shop',
        operation_description='Removing the product from the store price list',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'items': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='A comma-separated list of the external id of product info'
                )
            },
            required=['items']
        ),
        responses={200: 'True',
                   400: False}
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
    """
    Class for receiving a list of stores
    with the active status of receiving orders.
    """
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class CategoryView(ListAPIView):
    """
    Class for receiving a list of categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductInfoView(APIView):
    """
    Class for searching a product in the app.
    """
    @swagger_auto_schema(
        operation_summary='Products search',
        operation_description='Searching and receiving a list of products '
                              'according to the specified parameters.',
        manual_parameters=[
            yasg_param('shop_id', IN_PATH, type='int'),
            yasg_param('category_id', IN_PATH, type='int'),
        ],
        responses={200: openapi.Response(description='Orders',
                                         schema=ProductInfoSerializer(many=True)
                                         )
                   },
    )
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
    """
    Class for work with user's basket:
    :get: Receiving info about the user's products in a basket.
    :post: Adding products into the user's basket.
    :put: Changing products in user's basket.
    :delete: Removing a product from a user's basket.
    """
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_summary='List of products in Basket',
        operation_description='Receiving info about the user products in a basket.',
        responses={200: openapi.Response(description='Orders',
                                         schema=OrderSerializer(many=True),
                                         total_sum=openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                  description='Total order price')
                                         )
                   }
    )
    def get(self, request, *args, **kwargs):

        basket = Order.objects.filter(
            user_id=request.user.id, state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Adding products in Basket',
        operation_description='Adding products into the user basket',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'items': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    default='[{"product_info": ... , "quantity": ...}, ...]',
                    description='List from id of product info and quantity in dict format'
                )
            },
            required=['items']
        ),
        responses={201: 'True',
                   400: False}
    )
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

    @swagger_auto_schema(
        operation_summary='Delete products in Basket',
        operation_description='Removing a product from a user basket',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'items': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    default='"items": "id", ...',
                    description='A comma-separated list of the id product info'
                )
            },
            required=['items']
        ),
        responses={200: 'True',
                   400: False}
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

    @swagger_auto_schema(
        operation_summary='Change products in Basket',
        operation_description='Changing products in user basket',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'items': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    default='[{"id": int, "quantity": int}, ]',
                    description='List from id of product info and quantity'
                )
            },
            required=['items']
        ),
        responses={200: 'True',
                   400: False}
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
                    if type(order_item['id']) is int and type(order_item['quantity']) is int:
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
    """
    Class for confirm user's order and receiving confirm order.
    :get: Receiving all user orders or the specific order,
    :post: Confirm user's order.
    """
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_summary='Orders list',
        operation_description='Receiving the user order list',
        responses={200: openapi.Response(description='Orders',
                                         schema=OrderSerializer(many=True),
                                         total_sum=openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                  description='Total order price')
                                         )
                   }
    )
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

    @swagger_auto_schema(
        operation_summary='Accept orders',
        operation_description='Order confirmation and assignment of the "new" status',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='user order id'
                ),
                'contact': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='id of the created users contact'
                )
            },
            required=['id', 'contact']
        ),
        responses={201: 'True',
                   400: False}
    )
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
    """
    Class for changing status of the user's order
    """
    permission_classes = (IsCustomAdminUser,)

    @swagger_auto_schema(
        operation_summary='Change state of order',
        operation_description='Changing the status of a specific user order',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='order id'
                ),
                'state': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=[state[0] for state in STATE_CHOICES]
                )
            },
            required=['id', 'state']
        ),
        responses={200: 'True',
                   400: 'Указанны не все поля'}
    )
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


class CreateNewUserImage(APIView):
    """
    Class for updating a user's image
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        operation_summary='Change user image',
        operation_description='Updating image in user profile',
        manual_parameters=[
            openapi.Parameter(
                name='image',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='File with image. Max size image up to 800x800'
            )
        ],
        responses={
            200: 'OK',
            400: False
        }
    )
    def post(self, request, *args, **kwargs):
        if 'image' in self.request.FILES:

            user = request.user
            image = self.request.FILES["image"]
            old_image = user.image

            data = {
                'image': image
            }
            serializer = ImageSerializers(data=data)
            if serializer.is_valid():
                delete_image(old_image)
                user.image = image
                user.save()
                return JsonResponse(
                    {
                        'Status': 'OK',
                        'message': 'Картинка успешно загружена'
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse(
            {'Status': False, 'message': 'Не переданы основные аргументы'},
            status=status.HTTP_400_BAD_REQUEST
        )


class CreateNewProductInfoImage(APIView):
    """
    Class for updating a photo of the shop's product
    """
    permission_classes = (IsAuthenticated, IsShopUser)
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        operation_summary='Change product image',
        operation_description='Updating image in product info',
        manual_parameters=[
            openapi.Parameter(
                name='image',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='File with image. Max size image up to 800x800'
            ),
            openapi.Parameter(
                name='external_id',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                required=True,
                description='The external id of the product info'
            )
        ],
        responses={
            200: 'OK',
            400: False
        }
    )
    def post(self, request):

        if 'image' in self.request.FILES and 'external_id' in self.request.data:

            product = get_object_or_404(
                ProductInfo,
                shop=request.user.shop,
                external_id=self.request.data['external_id']
            )
            old_image = product.photo
            image = self.request.FILES['image']

            data = {
                'image': image
            }

            serializer = ImageSerializers(data=data)
            if serializer.is_valid():
                delete_image(old_image)
                product.photo = image
                product.save()

                return JsonResponse(
                    {
                        'Status': 'OK',
                        'message': 'Фото успешно загружено'
                    },
                    status=status.HTTP_201_CREATED
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse(
            {
                'Status': False,
                'message': 'Не переданы основные аргументы'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
