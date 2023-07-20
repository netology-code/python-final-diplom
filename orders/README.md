[Описание проекта](../README.md)

Запуск проекта: 

1. Создать виртуальное окружение, установить зависимости, при необходимости поменять значения в `orders/.env`
2. Создать базу данных 
```bash
createdb -U postgres diploma
```
3. Провести миграции 
```bash
python orders/manage.py migrate
```
Для silk:
```bash
python orders/manage.py collectstatic
```
4. Запустить redis
```bash
redis-server
redis-cli
```
5. Запустить celery 
```bash
celery -A orders.orders worker --loglevel=info
```
6. Запустить приложение 
```bash 
python orders/manage.py runserver
```
7. Посылать запросы на сервер можно через готовую коллекцию [postman-collection](../postman_collection.json)
8. Запустить тесты
```bash
pytest
```