from sqlite3 import IntegrityError

from orders.models import Order, OrderItem
from django.db.models import Q, F, Sum
from django.http import JsonResponse
from rest_framework.response import Response

from rest_framework.views import APIView
from ujson import loads as load_json

from pprint import pprint
from orders.serializers import OrderSerializer, OrderItemSerializer


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
            return JsonResponse({'Status': False,
                                 'Error': 'Log in required'},
                                status=403)

        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
                print("items_dict")
                pprint(items_dict)
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
                return JsonResponse({'Status': True,
                                     'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False,
                             'Errors': 'Не указаны все необходимые аргументы'})

    # добавить позиции в корзину
    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False,
                                 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')

        if items_sting:
            try:
                print('items_sting:')
                pprint(items_sting)
                items_dict = load_json(items_sting)
                print('items_dict:')
                pprint(items_dict)
            except ValueError:
                return JsonResponse({'Status': False,
                                     'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_updated = 0
                for order_item in items_dict:
                    print('order_item:')
                    print(order_item)
                    print(f"order_item['id']: {order_item['id']}")
                    print(f"order_item['quantity']: {order_item['quantity']}")
                    if type(order_item['id']) == int and type(order_item['quantity']) == int:
                        try:
                            objects_updated += OrderItem.objects.filter(order_id=basket.id,
                                                                        id=order_item['id']) \
                                .update(quantity=order_item['quantity'])
                        except ValueError:
                            return JsonResponse({'Status': False,
                                                 'Errors': 'Неверный формат запроса'})
                    else:
                        return JsonResponse({'Status': False,
                                             'Errors': 'Неверный формат запроса'})

                return JsonResponse({'Status': True, 'Обновлено объектов': objects_updated})

        return JsonResponse({'Status': False,
                             'Errors': 'Не указаны все необходимые аргументы (items_sting)'})
