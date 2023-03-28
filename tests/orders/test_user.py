# from pprint import pprint

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from orders.models import User
from model_bakery import baker
from rest_framework.authtoken.models import Token

# from django.urls import reverse
# from orders.api_urls import app_name
# from pprint import pprint

base_url = 'http://localhost:8000/api/v1/user/'


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        "first_name": "test",
        "last_name": "test_last",
        "email": "test@gmail.com",
        "password": "adminadmin",
        "company": "Test",
        "position": "funcionario",
        "user_type": "shop",
    }


@pytest.fixture
def user_factory():
    def factory(*args, **kwargs):
        return baker.make(User, *args, **kwargs)

    return factory


@pytest.fixture
def logged_user_factory(client):
    def factory(*args, **kwargs):
        user = baker.make(User,
                          *args,
                          **kwargs)
        user.is_active = True
        user.email_is_verified = True
        token = Token.objects.create(user=user)

        client.get(path=f'{base_url}verify_email/{token}/')

        return token

    return factory


@pytest.mark.django_db
def test_create_user(client, user_data, user_factory):
    user_count = User.objects.count()
    response = client.post(path=f'{base_url}register',
                           data=user_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get('Message') == 'Check your email to complete registration.'

    user_count += 1
    assert User.objects.count() == user_count

    user_factory(_quantity=10)
    assert User.objects.count() == user_count + 10


@pytest.mark.django_db
def test_user_login(client, user_factory):
    user = user_factory()

    response = client.post(
        f'{base_url}login',
        data={
            "email": user.email,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = client.post(
        f'{base_url}login',
        data={
            "email": user.email,
            "password": user.password,
        },
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_logged_user(client, logged_user_factory):
    token = logged_user_factory()
    response = client.get(f'{base_url}details')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'HTTP_AUTHORIZATION': f"Token {token.key}"}
    response = client.get(f'{base_url}details', **headers)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_user(client, user_factory):
    user = user_factory()
    response = client.get(f'{base_url}details')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    token, _ = Token.objects.get_or_create(user=user)

    response = client.get(path=f'{base_url}verify_email/{token}/')
    assert response.status_code == status.HTTP_200_OK

    headers = {'HTTP_AUTHORIZATION': f"Token {token.key}"}
    response = client.get(f'{base_url}details', **headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('email') == user.email


@pytest.mark.django_db
def test_user_contacts(client,
                       logged_user_factory):
    token = logged_user_factory()

    # get
    response = client.get(f'{base_url}details')

    print(f'token.user.pk: {token.user.pk}')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'HTTP_AUTHORIZATION': f"Token {token.key}"}

    response = client.get(f'{base_url}contact', follow=True, **headers)

    assert response.status_code == status.HTTP_200_OK

    contacts_count = response.data.get('count')
    assert contacts_count == 0

    # post
    response = client.post(f'{base_url}contact/',
                           follow=True,
                           data={
                               'city': 'city',
                               'street': 'street',
                               'house': 'house',
                               'structure': 'structure',
                               'building': 'building',
                               'apartment': 'apartment',
                               'phone': '+phone',
                               'user': token.user,
                           },
                           **headers)
    assert response.status_code == status.HTTP_201_CREATED

    contact_id = response.data.get('id')
    assert contact_id != 0

    response = client.get(f'{base_url}contact', follow=True, **headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('count') == contacts_count + 1

    # put
    response = client.put(f'{base_url}contact/{contact_id}',
                          follow=True,
                          data={
                              'city': 'new_city',
                              'street': 'street',
                              'house': 'house',
                              'structure': 'structure',
                              'building': 'building',
                              'apartment': 'apartment',
                              'phone': '+phone',
                              'user': str(token.user.id),
                              'id': str(contact_id),
                          },
                          **headers)

    assert response.status_code == status.HTTP_200_OK

    # delete
    response = client.delete(f'{base_url}contact/',
                             data={
                                 'items': str(contact_id),
                             },
                             follow=True, **headers)

    assert response.status_code == status.HTTP_200_OK

    response = client.get(f'{base_url}contact', follow=True, **headers)

    assert response.data.get('count') == contacts_count


@pytest.mark.django_db
def test_user_details(client, logged_user_factory):
    token = logged_user_factory()
    user_id = token.user.id
    headers = {'HTTP_AUTHORIZATION': f"Token {token.key}"}

    response = client.get(f'{base_url}details', follow=True, **headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('id') == user_id

    response = client.post(f'{base_url}details',
                           data={
                               'first_name': 'new_name',
                           },
                           follow=True,
                           **headers)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data.get('first_name') == 'new_name'


@pytest.mark.django_db
def test_user_password_reset(client, logged_user_factory):
    token = logged_user_factory()
    user_email = token.user.email

    response = client.post(f'{base_url}password_reset',
                           data={
                               'email': user_email,
                           },
                           follow=True)
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('Message') == "Check your email.."

    response = client.post(f'{base_url}password_reset/confirm',
                           data={
                               'email': user_email,
                               'password': 'qwer1234A',
                               'token': token,
                           },
                           follow=True)
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('Message') == "Password was changed."
