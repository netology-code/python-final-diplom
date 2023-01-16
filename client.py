import requests
from pprint import pprint

url = 'http://127.0.0.1:8000'

# request = requests.post(f'{url}/user/register',
#                   data={
#                       "first_name": "magaz",
#                       "last_name": "magaz3",
#                       "email": "magaz3@gmail.com",
#                       "password": "adminadmin",
#                       "company": "Magaz3",
#                       "position": "funcionario"
#                   })
#
# data_str = request.json()
# print("request:")
# pprint(data_str)

request = requests.post(f'{url}/user/login',
                        headers={
                            # 'Authorization': f'Token 173b6ba6cceccf285f952d2ab5a648c89c20df3b'
                        },

                        data={
                            "email": "magaz3@gmail.com",
                            "password": "adminadmin",
                        },
                        )
data_str = request.json()
print("request:")
pprint(data_str)

TOKEN = data_str.get('Token')
print(f'TOKEN: {TOKEN}')

# request = requests.get(url,
#                  headers={
#                      'Authorization': f'Token {TOKEN}'
#                  }
#                  )
# print("request:")
# pprint(request.json())
