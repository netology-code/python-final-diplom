import os

import pytest

from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from backend.models import ConfirmEmailToken, User
from backend.serializers import UserSerializer
from backend.tasks import delete_image
from tests.conftest import headers_token


@pytest.mark.parametrize(
    ['test_email', 'test_password', 'test_type', 'status_code'], (
            ('1', '1', 'bayer', HTTP_400_BAD_REQUEST),
            ('', '', 'shop', HTTP_201_CREATED),
            ('', '', 'test', HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_user_registration(django_user_model, client, test_email, test_password, test_type, status_code):
    url = reverse('backend:user-register')
    data = {
        'email': test_email or 'example@asd.com',
        'password': test_password or 'sm59efp5',
        'first_name': 'Oleg',
        'last_name': 'Sungurov',
        'company': 'Microsoft',
        'position': 'engineer',
        'type': test_type or 'shop',
        'image': {}
    }
    response = client.post(url, data)

    assert response.status_code == status_code
    if response.status_code != HTTP_400_BAD_REQUEST:
        new_user = django_user_model.objects.get(email=data['email'])
        assert new_user.type == test_type
        assert new_user.is_active is False


@pytest.mark.parametrize(
    ['test_email', 'test_token', 'status_code'], (
            ('', '', HTTP_200_OK),
            ('123', '', HTTP_400_BAD_REQUEST),
            ('', 'asxklcgbauyhgsbd', HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_confirm_account(client, create_bayer_user, test_email, test_token, status_code):
    user = create_bayer_user
    url = reverse('backend:confirm-email')
    token = ConfirmEmailToken.objects.create(user=user)
    data = {
        'email': test_email or user.email,
        'token': test_token or token.key,
    }

    response = client.post(url, data)
    new_user = User.objects.get(email=user.email)

    assert response.status_code == status_code
    if response.status_code != HTTP_400_BAD_REQUEST:
        assert new_user.is_active is True


@pytest.mark.parametrize(
    ['email', 'password', 'status_code'], (
            ('', '', HTTP_200_OK),
            ('test@email.com', '', HTTP_400_BAD_REQUEST),
            ('', 'test-password', HTTP_400_BAD_REQUEST)
    )
)
@pytest.mark.django_db
def test_login_account(client, create_user_is_active, email, password, status_code):
    url = reverse('backend:login-account')
    user = create_user_is_active
    data = {
        'email': email or user.email,
        'password': password or 'asdhakfosaf',
    }

    response = client.post(url, data)

    assert response.status_code == status_code
    if response.status_code != HTTP_400_BAD_REQUEST:
        assert 'Token' in response.json()


@pytest.mark.django_db
def test_get_account_details(client, get_token):
    url = reverse('backend:account-info')
    token = get_token
    serializer = UserSerializer(data=token.user)
    if serializer.is_valid():
        response = client.get(path=url, headers=headers_token(token))

        assert response.status_code == HTTP_200_OK
        assert response.json() == serializer.data


@pytest.mark.parametrize(
    ['password', 'status_code'], (
            ('', HTTP_201_CREATED),
            ('123', HTTP_400_BAD_REQUEST),
            ('asdhakfosaf', HTTP_201_CREATED)
    )
)
@pytest.mark.django_db
def test_update_account_details(client, get_token, password, status_code):
    url = reverse('backend:account-info')
    token = get_token
    data = {
        'password': password or 'qweasdzxc1234',
        'first_name': 'Andrey'
    }

    response = client.post(path=url, headers=headers_token(token), data=data)

    assert response.status_code == status_code
    if response.status_code != HTTP_400_BAD_REQUEST:
        assert response.json()['first_name'] == 'Andrey'
@pytest.mark.django_db
def test_logout(client, get_token):
    url = reverse('backend:logout')
    token = get_token
    count = Token.objects.count()

    response = client.get(path=url, headers=headers_token(token))

    assert response.status_code == HTTP_204_NO_CONTENT
    assert Token.objects.count() == count - 1


@pytest.mark.parametrize(
    ['file_end', 'status_code', ], (
            ('.png', HTTP_201_CREATED),
            ('.exe', HTTP_400_BAD_REQUEST),
            ('.jpg', HTTP_201_CREATED)
    )
)
@pytest.mark.django_db
def test_upload_user_image(client, get_token, file_end, status_code, settings):
    url = reverse('backend:account-image')
    token = get_token
    old_list_files = os.listdir(settings.MEDIA_ROOT + '/image/user_image')
    with open(settings.TEST_IMAGE_PATH + 'test_image' + file_end, 'rb') as file:
        data = {
            'image': file
        }

        response = client.post(url, headers=headers_token(token), data=data, format="multipart")

    assert response.status_code == status_code
    if response.status_code != HTTP_400_BAD_REQUEST:
        user = User.objects.get(id=token.user.id)
        image_name = user.image.name.split('/')[-1]
        new_list_file = os.listdir(settings.MEDIA_ROOT + '/image/user_image')
        delete_image(user.image)
        assert image_name in new_list_file
        assert len(new_list_file) == len(old_list_files) + 1

