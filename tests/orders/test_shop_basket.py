# import pytest
# from rest_framework.test import APIClient
# from model_bakery import baker
# from rest_framework import status
# from rest_framework.authtoken.models import Token
# from orders.models import User
#
# from .test_utils import base_url, base_url_user
#
#
# @pytest.fixture
# def client():
#     return APIClient()
#
#
# @pytest.fixture
# def user_4_shop_factory(client):
#     def factory(*args, **kwargs):
#         user = baker.make(User, *args, **kwargs)
#         token = Token.objects.create(user=user)
#         return user, token
#
#     return factory
#
#
# @pytest.fixture
# def shop_factory(client, user_4_shop_factory):
#     def factory(*args, **kwargs):
#         user, token = user_4_shop_factory()
#
#         response = client.get(path=f'{base_url_user}verify_email/{token}/')
#
#         headers = {'HTTP_AUTHORIZATION': f"Token {token.key}"}
#
#         response = client.post(f'{base_url_user}details',
#                                data={
#                                    'user_type': 'shop',
#                                },
#                                follow=True,
#                                **headers)
#         user_id = response.data.get('id')
#         user = User.objects.get(pk=user_id)
#
#         return user, token
#
#     return factory
#
#
# @pytest.mark.django_db
# def test_shops_list(client, shop_factory):
#     response = client.get(path=f'{base_url}shops')
#
#     assert response.status_code == status.HTTP_200_OK
#
#     shops_count = response.data.get('count')
#
#     user, token = shop_factory()
#     print(f'user.user_type: {user.user_type}')
#
#     response = client.get(path=f'{base_url}shops')
#
#     assert response.data.get('count') >= shops_count
