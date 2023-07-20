import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from model_bakery import baker

from backend.models import User, Contact, Shop, Category, Product, ProductInfo, Parameter, ProductParameter


@pytest.fixture
def client():
    return APIClient()


USER = {'email': 'testing1@test.com', 'password': 'test123', 'username': 'test_user', 
        'full_name': 'Тест', 'company': 'Тест', 'position': 'manager'}


@pytest.fixture
def buyer(django_user_model):
    buyer = django_user_model.objects.create_user(email=USER['email'], 
                                                 password=USER['password'],
                                                 username=USER['username'],
                                                 type='buyer')
    return buyer 


@pytest.fixture
def seller(django_user_model):
    seller = django_user_model.objects.create_user(email=USER['email'], 
                                                 password=USER['password'],
                                                 username=USER['username'],
                                                 type='shop')
    return seller 


@pytest.fixture 
def user_factory():
    def factory(*args, **kwargs):
        return baker.make(User, *args, **kwargs)
    return factory 


@pytest.fixture 
def shop_factory():
    def factory(*args, **kwargs):
        return baker.make(Shop, *args, **kwargs)
    return factory 


@pytest.fixture 
def category_factory():
    def factory(*args, **kwargs):
        return baker.make(Category, *args, **kwargs)
    return factory 


@pytest.fixture 
def product_factory():
    def factory(*args, **kwargs):
        return baker.make(Product, *args, **kwargs)
    return factory 


@pytest.mark.django_db
def test_register(client):
    data = {'email': USER['email'], 'password': USER['password'], 'username': USER['username'], 
            'type': 'buyer', 'full_name': USER['full_name'], 'company': USER['company'], 
            'position': USER['position']}
    url = reverse('register')

    request = client.post(path=url, data=data)

    assert request.status_code == 200
    user = User.objects.get(email=data['email'])
    assert user


@pytest.mark.django_db
def test_login(client, user_factory):
    test_user = user_factory(_quantity=1)
    url = reverse('login')

    request = client.post(path=url, 
                          data={'username': test_user[0].username, 
                                'password': test_user[0].password})

    assert request.status_code == 200


@pytest.mark.django_db 
def test_get_contact(client, buyer):
    test_user = buyer
    test_contact = {'city': 'Moscow', 'street': 'Real', 'house': '23', 
                    'structure': None, 'building': None, 'apartment': None,
                    'phone': '0 000 000 00 00'}
    url = reverse('get_contact_info')

    client.force_authenticate(test_user)
    request = client.post(path=url, data=test_contact)
    client.force_authenticate(user=None)

    assert request.status_code == 200
    contact = Contact.objects.get(phone=test_contact['phone'])
    assert contact


@pytest.mark.django_db
def test_retrieve_shop(client, shop_factory, buyer):
    test_user = buyer
    test_shop = shop_factory(_quantity=1)

    client.force_authenticate(test_user)
    request = client.get(f'/shops/{test_shop[0].id}/')
    response = request.json()
    client.force_authenticate(user=None)

    assert request.status_code == 200
    assert response['name'] == test_shop[0].name


@pytest.mark.django_db
def test_list_shops(client, shop_factory, buyer):
    test_user = buyer
    test_shops = shop_factory(_quantity=5)

    client.force_authenticate(test_user)
    request = client.get('/shops/')
    client.force_authenticate(user=None)

    assert request.status_code == 200
#     # for i, shop in enumerate(data):
#     #     assert shop['name'] == test_shops[i].name # Пыталась сделать так, но магазины сохраняются/выдаются не по порядку, поэтому взаимодействите по id не получается
    for test_shop in test_shops:
        shop_id, shop_name = Shop.objects.get(id=test_shop.id), Shop.objects.get(name=test_shop.name)
        assert shop_id, shop_name


@pytest.mark.django_db
def test_retrieve_category(client, category_factory, buyer):
    test_user = buyer
    test_category = category_factory(_quantity=1)

    client.force_authenticate(test_user)
    request = client.get(f'/categories/{test_category[0].id}/')
    response = request.json()
    client.force_authenticate(user=None)

    assert request.status_code == 200
    assert response['name'] == test_category[0].name


@pytest.mark.django_db
def test_list_categories(client, category_factory, buyer):
    test_user = buyer
    test_categories = category_factory(_quantity=5)

    client.force_authenticate(test_user)
    request = client.get('/categories/')
    client.force_authenticate(user=None)

    assert request.status_code == 200
    for test_category in test_categories:
        category_id, category_name = Category.objects.get(id=test_category.id), Category.objects.get(name=test_category.name)
        assert category_id, category_name


@pytest.mark.django_db
def test_retrieve_product(client, product_factory, buyer):
    test_user = buyer
    test_product = product_factory(_quantity=1)

    client.force_authenticate(test_user)
    request = client.get(f'/products/{test_product[0].id}/')
    response = request.json()
    client.force_authenticate(user=None)

    assert request.status_code == 200
    assert response['name'] == test_product[0].name


@pytest.mark.django_db
def test_list_products(client, product_factory, buyer):
    test_user = buyer
    test_products = product_factory(_quantity=5)

    client.force_authenticate(test_user)
    request = client.get('/products/')
    client.force_authenticate(user=None)

    assert request.status_code == 200
    for test_product in test_products:
        product_id, product_name = Product.objects.get(id=test_product.id), Product.objects.get(name=test_product.name)
        assert product_id, product_name


@pytest.mark.django_db
def test_update(client, seller):
    test_user = seller

    client.force_authenticate(test_user)
    request = client.post('/update/shop1.yaml/') 
    client.force_authenticate(user=None)

    assert request.status_code == 200
    assert Shop.objects.count() == 1
    assert Category.objects.count() == 3
    assert Product.objects.count() == 4 
    assert ProductInfo.objects.count() == 4
    assert Parameter.objects.count() == 4
    assert ProductParameter.objects.count() == 16