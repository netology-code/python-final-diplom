from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from custom_auth.models import User, Contact, ConfirmEmailToken
from .models import Category, Product, Shop, Order


class ApiTests(APITestCase):
    user_data = {
        'first_name': 'Ivan',
        'last_name': 'Ivanov',
        'email': '123@123.ru',
        'password': 'Kill1234',
        'company': 'Samsung',
        'position': 'manager',
        'type': 'buyer'
    }

    def test_register_user(self):
        count = User.objects.count()
        url = reverse('shop:user-register')
        response = self.client.post(url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['Status'], True)
        self.assertEqual(User.objects.count(), count + 1)

    def test_user_confirm(self):
        user = User.objects.create_user(
            first_name='Ivan',
            last_name='Ivanov',
            email='123@123.ru',
            password='Kill1234',
            company='Samsung',
            position='manager',
        )
        token = ConfirmEmailToken.objects.create(user_id=user.id).key
        url = reverse('shop:user-register-confirm')
        data = {'email': user.email, 'token': token}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)

    def test_contact_user(self):
        user = User.objects.create_user(
            first_name='Ivan',
            last_name='Ivanov',
            email='123@123.ru',
            password='Kill1234',
            company='Samsung',
            position='manager',
            is_active=True
        )
        url = reverse('shop:user-contact')
        token = Token.objects.create(user=user).key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        data = {
            'city': 'Moscow',
            'street': 'Tverskaya',
            'house': '11',
            'apartment': '22',
            'phone': '+79991112233'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Contact.objects.get(user_id=user.id).phone, data['phone'])

    def test_partner_update_and_state(self):
        user = User.objects.create_user(
            first_name='Ivan',
            last_name='Ivanov',
            email='123@123.ru',
            password='Kill1234',
            company='Samsung',
            position='manager',
            type='shop',
            is_active=True
        )
        url = reverse('shop:partner-update')
        url_state = reverse('shop:partner-state')
        token = Token.objects.create(user=user).key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        data_update = {
            'partner': user.id,
            'url': 'https://raw.githubusercontent.com/netology-code/pd-diplom/master/data/shop1.yaml'
        }
        response = self.client.post(url, data_update)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)

        data_state = {'partner': user.id, 'state': True}
        response_state = self.client.post(url_state, data_state)

        self.assertEqual(response_state.status_code, status.HTTP_200_OK)
        self.assertEqual(response_state.json()['Status'], True)

    def test_product_info(self):
        url = reverse('shop:products-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('Errors', response.data)

    def test_add_to_basket(self):
        self.test_partner_update_and_state()
        user = User.objects.get(email='123@123.ru')
        url = reverse('shop:basket')
        id_ = 2
        quantity = 5
        response = self.client.put(url, {'items': [{'id': id_, 'quantity': quantity}]}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Order.objects.filter(user_id=user.id, status='basket').exists())
        self.assertEqual(response.json()['Status'], True)
        self.assertIn('Status', response.json())

    def test_basket(self):
        self.test_add_to_basket()
        url = reverse('shop:basket')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
