import os

import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from backend.models import (Category, Contact, Order, OrderItem, Parameter, Product, ProductInfo, ProductParameter,
                            Shop)
from backend.tasks import delete_image
from tests.conftest import URL_SHOP, headers_token


@pytest.mark.parametrize(
    ['phone', 'test_count', 'status_code'], (
            ('', 1, HTTP_201_CREATED),
            ([1, 2, 3], 0, HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_post_contacts(client, get_token, model_factory, phone, test_count, status_code):
    url = reverse('backend:contact')
    token = get_token
    count = Contact.objects.count()
    data = {
        'city': 'test_city',
        'street': 'test_street',
        'phone': phone or '+73338882244',
    }

    response = client.post(path=url, headers=headers_token(token), data=data)

    assert response.status_code == status_code
    if response.status_code != HTTP_400_BAD_REQUEST:
        assert Contact.objects.count() == count + test_count


@pytest.mark.django_db
def test_get_contact(client, get_token, model_factory):
    url = reverse('backend:contact')
    token = get_token
    model_factory(Contact, user=token.user)

    response = client.get(path=url, headers=headers_token(token))

    assert response.status_code == HTTP_200_OK
    assert {'phone'}.issubset(response.json()[0])


@pytest.mark.parametrize(
    ['items', 'test_count', 'status_code'], (
            ('', 2, HTTP_200_OK),
            ('123,345,1533', 0, HTTP_200_OK),
            ('test', 0, HTTP_400_BAD_REQUEST)
    )
)
@pytest.mark.django_db
def test_delete_contacts(client, get_token, model_factory, items, test_count, status_code):
    url = reverse('backend:contact')
    token = get_token
    model_factory(Contact, user=token.user, _quantity=3)
    count = Contact.objects.count()
    contacts = Contact.objects.all().values('id')
    list_delete = [str(contact['id']) for contact in contacts]
    data = {
        'items': items or ','.join(list_delete[:2])
    }

    response = client.delete(path=url, headers=headers_token(token), data=data)

    assert response.status_code == status_code
    if response.status_code != HTTP_400_BAD_REQUEST:
        assert response.json()['Удалено объектов'] == test_count
        assert count == Contact.objects.count() + test_count


@pytest.mark.parametrize(
    ['contact_id', 'status_code'], (
            ('', HTTP_200_OK),
            (123, HTTP_400_BAD_REQUEST),
            ('test', HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_put_contact(client, get_token, model_factory, contact_id, status_code):
    url = reverse('backend:contact')
    token = get_token
    model_factory(Contact, user=token.user)
    contact = Contact.objects.get(user=token.user)
    data = {
        'id': contact_id or str(contact.id),
        'structure': 'test_structure',
        'city': 'test_city'
    }

    response = client.put(path=url, headers=headers_token(token), data=data)
    up_contact = Contact.objects.get(id=contact.id)
    assert response.status_code == status_code
    if response.status_code != HTTP_400_BAD_REQUEST:
        assert up_contact.structure == 'test_structure'
        assert up_contact.city == 'test_city'


@pytest.mark.django_db
def test_get_shop_state(client, get_shop_token, model_factory):
    url = reverse('backend:partner-state')
    token = get_shop_token
    shop = model_factory(Shop, user=token.user)

    response = client.get(path=url, headers=headers_token(token))

    assert response.status_code == HTTP_200_OK
    assert response.json()['name'] == shop.name


@pytest.mark.parametrize(
    ['state', 'status_code'], (
            (False, HTTP_201_CREATED),
            (1234, HTTP_400_BAD_REQUEST),
            ('test', HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_post_shop_state(client, get_shop_token, model_factory, state, status_code):
    url = reverse('backend:partner-state')
    token = get_shop_token
    model_factory(Shop, user=token.user)
    data = {
        'state': str(state),
    }

    response = client.post(path=url, headers=headers_token(token), data=data)
    status = Shop.objects.get(user=token.user)

    assert response.status_code == status_code
    if response.status_code != HTTP_400_BAD_REQUEST:
        assert status.state is state


@pytest.mark.django_db
def test_get_partner_order(client, get_shop_token, model_factory, get_token):
    url = reverse('backend:partner-orders')
    token = get_shop_token
    token_user = get_token
    shop = model_factory(Shop, user=token.user)
    contact = model_factory(Contact, user=token_user.user)
    category = model_factory(Category, shops=[shop])
    product = model_factory(Product, category=category)
    product_info = model_factory(ProductInfo, product=product, shop=shop, price=1200)
    order = model_factory(Order, state='new', user=token_user.user, contact=contact)
    model_factory(OrderItem, order=order, product_info=product_info, quantity=12)

    response = client.get(path=url, headers=headers_token(token))

    assert response.status_code == HTTP_200_OK
    assert len(response.data) == 1


@pytest.mark.parametrize(
    ['test_url', 'status', 'status_code'], (
            ('', True, HTTP_201_CREATED),
            ('https://www.youtube.com/', False, HTTP_201_CREATED),
            ('1234', False, HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_post_partner_update(client, get_shop_token, test_url, status, status_code):
    url = reverse('backend:partner-update')
    token = get_shop_token
    count_shop = Shop.objects.count()
    count_category = Category.objects.count()
    count_product = Product.objects.count()
    count_product_info = ProductInfo.objects.count()
    data = {
        'url': test_url or URL_SHOP
    }

    response = client.post(path=url, headers=headers_token(token), data=data)

    assert response.status_code == status_code
    assert response.json()['Status'] is status
    if response.json()['Status']:
        assert Shop.objects.count() == count_shop + 1
        assert Category.objects.count() == count_category + 3
        assert Product.objects.count() == count_product + 4
        assert ProductInfo.objects.count() == count_product_info + 4


@pytest.mark.parametrize(
    ['test_id', 'quantity', 'status_code'], (
            ('', '', HTTP_200_OK),
            (212, '', HTTP_400_BAD_REQUEST),
            ('test1', 'test2', HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_put_partner_update(client, get_shop_token, model_factory, test_id, quantity, status_code):
    url = reverse('backend:partner-update')
    token = get_shop_token
    shop = model_factory(Shop, user=token.user)
    category = model_factory(Category, shops=[shop])
    product = model_factory(Product, category=category)
    product_info = model_factory(ProductInfo, product=product, shop=shop)
    data = {
        'id': test_id or product_info.external_id,
        'quantity': quantity or 20,
    }

    response = client.put(path=url, headers=headers_token(token), data=data)
    new_quantity = ProductInfo.objects.get(external_id=product_info.external_id).quantity

    assert response.status_code == status_code
    if response.status_code != HTTP_400_BAD_REQUEST:
        assert new_quantity == 20


@pytest.mark.parametrize(
    ['items', 'count', 'status_code'], (
            ('123,126,17', 0, HTTP_200_OK),
            ('', 2, HTTP_200_OK),
            ('test', 0, HTTP_400_BAD_REQUEST)
    )
)
@pytest.mark.django_db
def test_delete_partner_update(client, get_shop_token, model_factory, items, count, status_code):
    url = reverse('backend:partner-update')
    token = get_shop_token
    shop = model_factory(Shop, user=token.user)
    category = model_factory(Category, shops=[shop])
    products = model_factory(Product, category=category, _quantity=2)
    product_infos = [model_factory(ProductInfo, product=product, shop=shop)
                     for product in products]
    list_external_id = [str(item.external_id) for item in product_infos]
    count_product_info = ProductInfo.objects.count()
    data = {
        'items': items or ','.join(list_external_id),
    }

    response = client.delete(path=url, headers=headers_token(token), data=data)
    new_count_product_info = ProductInfo.objects.count()

    assert response.status_code == status_code
    if status_code != HTTP_400_BAD_REQUEST:
        assert response.json()['Удалено объектов'] == count
        assert new_count_product_info == count_product_info - count


@pytest.mark.django_db
def test_get_shop_list(client, model_factory):
    url = reverse('backend:shop-list')
    model_factory(Shop, _quantity=3)

    response = client.get(url)

    assert response.status_code == HTTP_200_OK
    assert response.json()['count'] == 3


@pytest.mark.django_db
def test_get_category_list(client, model_factory):
    url = reverse('backend:categories')
    model_factory(Category, _quantity=15)

    response = client.get(url)

    assert response.status_code == HTTP_200_OK
    assert response.json()['count'] == 15


@pytest.mark.django_db
def test_list_product_info(client, model_factory):
    url = reverse('backend:product-info')
    shop = model_factory(Shop)
    category = model_factory(Category, shops=[shop])
    products = model_factory(Product, category=category, _quantity=15)
    for product in products:
        model_factory(ProductInfo, product=product, shop=shop)
    params = {
        'category_id': category.id,
        'shop_id': shop.id
    }

    response = client.get(path=url, params=params)

    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 15


@pytest.mark.django_db
def test_get_basket(client, get_token, model_factory):
    url = reverse('backend:basket')
    token = get_token
    shop = model_factory(Shop)
    category = model_factory(Category, shops=[shop])
    product = model_factory(Product, category=category)
    product_info = model_factory(ProductInfo, product=product, shop=shop, price=6543)
    parameter = model_factory(Parameter)
    model_factory(ProductParameter, product_info=product_info, parameter=parameter)
    order = model_factory(Order, user=token.user, state='basket')
    model_factory(OrderItem, product_info=product_info, quantity=2, order=order)

    response = client.get(path=url, headers=headers_token(token))

    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    assert len(response.json()[0]['ordered_items']) == 1
    assert {'total_sum', 'dt', 'state'}.issubset(response.json()[0])


@pytest.mark.parametrize(
    ['items', 'count', 'status_code'], (
            ('', 1, HTTP_201_CREATED),
            ('[{"product_info": "test", "quantity": 2}]', 0, HTTP_400_BAD_REQUEST),
            ('test', 0, HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_post_basket(client, get_token, model_factory, items, count, status_code):
    url = reverse('backend:basket')
    token = get_token
    shop = model_factory(Shop)
    category = model_factory(Category, shops=[shop])
    product = model_factory(Product, category=category)
    product_info = model_factory(ProductInfo, product=product, shop=shop, price=6543)
    parameter = model_factory(Parameter)
    model_factory(ProductParameter, product_info=product_info, parameter=parameter)
    count_order_item = OrderItem.objects.count()
    data = {
        'items': items or f'[{{"product_info": {product_info.id}, "quantity": 2}}]'
    }

    response = client.post(path=url, headers=headers_token(token), data=data)

    assert response.status_code == status_code
    if status_code != HTTP_400_BAD_REQUEST:
        assert response.json()['Создано объектов'] == count
        assert OrderItem.objects.count() == count_order_item + count


@pytest.mark.parametrize(
    ['order_item_id', 'quantity', 'count', 'status_code'], (
            (0, 0, 1, HTTP_200_OK),
            (12, '12', 0, HTTP_200_OK),
            (1, 'test', 0, HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_put_basket(client, get_token, model_factory, order_item_id, quantity, count, status_code):
    url = reverse('backend:basket')
    token = get_token
    shop = model_factory(Shop)
    category = model_factory(Category, shops=[shop])
    product = model_factory(Product, category=category)
    product_info = model_factory(ProductInfo, product=product, shop=shop, price=6543)
    parameter = model_factory(Parameter)
    model_factory(ProductParameter, product_info=product_info, parameter=parameter)
    order = model_factory(Order, user=token.user, state='basket')
    order_item = model_factory(OrderItem, product_info=product_info, quantity=10, order=order)
    data = {
        'items': f'[{{"id": {int(order_item_id or order_item.id)}, "quantity": {quantity or 2}}}]'
    }

    response = client.put(path=url, headers=headers_token(token), data=data)

    assert response.status_code == status_code
    if status_code != HTTP_400_BAD_REQUEST:
        assert response.json()['Обновлено объектов'] == count
    if count:
        assert OrderItem.objects.get(id=order_item.id).quantity == 2


@pytest.mark.parametrize(
    ['test_list', 'count'], (
            ('123,42,213,54', 0),
            ('', 4)
    )
)
@pytest.mark.django_db
def test_delete_basket(client, get_token, model_factory, test_list, count):
    url = reverse('backend:basket')
    token = get_token
    shop = model_factory(Shop, _quantity=4)
    order = model_factory(Order, user=token.user, state='basket')
    category = model_factory(Category)
    products = model_factory(Product, category=category, _quantity=4)
    products_shops = zip(shop, products)
    products_info = [model_factory(ProductInfo, shop=shop, product=product)
                     for shop, product in products_shops]
    orders_info = [model_factory(OrderItem, order=order, product_info=product_info)
                   for product_info in products_info]
    orders_info_list_id = [str(order_info.id)
                           for order_info in orders_info]
    count_orders_info = OrderItem.objects.count()
    data = {
        'items': test_list or ','.join(orders_info_list_id)
    }

    response = client.delete(path=url, headers=headers_token(token), data=data)
    new_count = OrderItem.objects.count()

    assert response.status_code == HTTP_200_OK
    assert response.json()['Удалено объектов'] == count
    assert new_count == count_orders_info - count


@pytest.mark.django_db
def test_get_order(client, get_token, model_factory):
    url = reverse('backend:order')
    token = get_token
    model_factory(Order, user=token.user, _quantity=3)

    response = client.get(path=url, headers=headers_token(token))

    assert response.status_code == HTTP_200_OK
    assert response.data


@pytest.mark.parametrize(
    ['pk', 'status_code'], (
            ('', HTTP_200_OK),
            ('32', HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_get_order_pk(client, get_token, model_factory, pk, status_code):
    token = get_token
    order = model_factory(Order, user=token.user)
    url = reverse('backend:order_pk', args=(order.id,))
    if pk:
        url = reverse('backend:order_pk', args=(pk,))

    response = client.get(path=url, headers=headers_token(token))

    assert response.status_code == status_code
    if status_code != HTTP_400_BAD_REQUEST:
        assert len(response.data) == 1
        assert {'id', 'ordered_items', 'state', 'total_sum'}.issubset(response.data[0])


@pytest.mark.parametrize(
    ['state', 'status_code', 'contact'],
    (
            ('new', HTTP_201_CREATED, ''),
            ('basket', HTTP_400_BAD_REQUEST, 'test'),
    )
)
@pytest.mark.django_db
def test_post_order(client, get_token, model_factory, state, status_code, contact):
    url = reverse('backend:order')
    token = get_token
    order = model_factory(Order, user=token.user, state='basket').id
    if not contact:
        contact = model_factory(Contact, user=token.user).id
    data = {
        'id': str(order),
        'contact': str(contact),
    }

    response = client.post(path=url, headers=headers_token(token), data=data)
    new_state = Order.objects.get(id=order).state

    assert response.status_code == status_code
    assert new_state == state


@pytest.mark.parametrize(
    ['state', 'status_code'],
    (
            ('assembled', HTTP_200_OK),
            ('test', HTTP_400_BAD_REQUEST),
            (1235, HTTP_400_BAD_REQUEST)
    )
)
@pytest.mark.django_db
def test_put_admin(client, get_admin_token, get_token, model_factory, state, status_code):
    url = reverse('backend:admin')
    token_admin = get_admin_token
    token_user = get_token
    order = model_factory(Order, user=token_user.user)
    data = {
        'id': str(order.id),
        'state': state,
    }

    response = client.put(path=url, headers=headers_token(token_admin), data=data)
    new_state = Order.objects.get(id=order.id).state

    assert response.status_code == status_code
    if status_code != HTTP_400_BAD_REQUEST:
        assert new_state == state
    elif status_code == HTTP_400_BAD_REQUEST:
        assert new_state != state
        assert response.json()['Error'] == 'Неверный статус'


@pytest.mark.parametrize(
    ['file_end', 'external_id', 'status_code'], (
            ('.png', '345162', HTTP_201_CREATED),
            ('.exe', '345162', HTTP_400_BAD_REQUEST),
            ('.jpg', '555555', HTTP_404_NOT_FOUND),
    )
)
@pytest.mark.django_db
def test_upload_product_image(client, get_shop_token, model_factory, file_end, external_id, status_code, settings):
    url = reverse('backend:product-image')
    token = get_shop_token
    user = token.user
    old_list_files = os.listdir(settings.MEDIA_ROOT + '/image/products_image')
    shop = model_factory(Shop, user=user)
    category = model_factory(Category)
    product = model_factory(Product, category=category)
    model_factory(ProductInfo, product=product, shop=shop, price=6543, quantity=4, external_id=345162)

    with open(settings.TEST_IMAGE_PATH + 'test_image' + file_end, 'rb') as file:
        data = {
            'image': file,
            'external_id': external_id
        }

        response = client.post(url, headers=headers_token(token), data=data, format="multipart")

    assert response.status_code == status_code
    if status_code != HTTP_400_BAD_REQUEST and status_code != HTTP_404_NOT_FOUND:
        product_info = ProductInfo.objects.get(external_id=external_id)
        new_product_image = product_info.photo.name.split('/')[-1]
        new_list_file = os.listdir(settings.MEDIA_ROOT + '/image/products_image')
        delete_image(product_info.photo)
        assert new_product_image in new_list_file
        assert len(new_list_file) == len(old_list_files) + 1
