import requests
from pprint import pprint

url = 'http://127.0.0.1:8000'

# Регистрация

# request = requests.post(f'{url}/user/register',
#                         data={
#                             "first_name": "magaz",
#                             "last_name": "magaz4",
#                             "email": "magaz4@gmail.com",
#                             "password": "adminadmin",
#                             "company": "Magaz4",
#                             "position": "funcionario"
#                         })
#
# data_str = request.json()
# print("request:")
# pprint(data_str)


# Вход
request = requests.post(f'{url}/user/login',
                        headers={
                            # 'Authorization': f'Token 173b6ba6cceccf285f952d2ab5a648c89c20df3b'
                        },

                        data={
                            "email": "magaz4@gmail.com",
                            "password": "adminadmin",
                        },
                        )
data_str = request.json()
print("request:")
pprint(data_str)

TOKEN = data_str.get('Token')
print(f'TOKEN: {TOKEN}')

# Список товаров
request = requests.get(f'{url}/products/list',
                       headers={
                           'Authorization': f'Token {TOKEN}',
                       },
                       data={
                           "page": "1",
                       },
                       )
print("products-list:")
pprint(request.json())

# Список магазинов
request = requests.get(f'{url}/shop/list',
                       headers={
                           'Authorization': f'Token {TOKEN}',
                       },
                       data={
                           "page": "1",
                       },
                       )
print("shop-list:")
pprint(request.json())

# Список товаров по категории и магазину
request = requests.get(f'{url}/products/view',
                       headers={
                           'Authorization': f'Token {TOKEN}',
                       },
                       data={
                           "page": "1",
                           'category': 'Смартфоны',
                           'shop': 'Связной',
                       },
                       )
print("products-view:")
pprint(request.json())

# Карточка товара
request = requests.get(f'{url}/product/view_by_id',
                       headers={
                           'Authorization': f'Token {TOKEN}',
                       },
                       data={
                           "id": "1",
                       },
                       )
print("products-view:")
pprint(request.json())
