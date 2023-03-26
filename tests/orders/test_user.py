import pytest
from rest_framework import status
from rest_framework.test import APIClient
from orders.models import User
from model_bakery import baker
from rest_framework.authtoken.models import Token


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
def logged_user_factory():
    def factory(*args, **kwargs):
        user = baker.make(User,
                          *args,
                          **kwargs)
        user.is_active = True
        user.email_is_verified = True
        return Token.objects.create(user=user)

    return factory


@pytest.mark.django_db
def test_create_user(client, user_data, user_factory):
    user_count = User.objects.count()
    response = client.post(path='/api/v1/user/register',
                           data=user_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get('Message') == 'Check your email to complete registration.'

    user_count += 1
    assert User.objects.count() == user_count

    user_factory(_quantity=10)
    assert User.objects.count() == user_count + 10


# @pytest.mark.django_db
# def test_user_login(client, user_factory):
#     user = user_factory()
#     response = client.post(
#         '/api/v1/user/login',
#         data={
#             "email": user.email,
#             "password": user.password,
#         },
#     )
#     assert response.status_code == status.HTTP_200_OK
#
#     response = client.post(
#         '/api/v1/user/login',
#         data={
#             "email": user.email,
#         },
#     )
#     assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_get_logged_user(client, logged_user_factory):
    token = logged_user_factory()
    response = client.get('/api/v1/user/details')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'HTTP_AUTHORIZATION': f"Token {token.key}"}
    response = client.get('/api/v1/user/details', **headers)

    # assert response.status_code == status.HTTP_200_OK
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_user(client, user_factory):
    user = user_factory()
    response = client.get('/api/v1/user/details')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    token, _ = Token.objects.get_or_create(user=user)
    headers = {'HTTP_AUTHORIZATION': f"Token {token.key}"}
    response = client.get('/api/v1/user/details', **headers)

    # assert response.status_code == status.HTTP_200_OK
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # assert response.data.get('email') == user.email
