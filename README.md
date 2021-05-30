# Дипломная работа к профессии Python-разработчик «API Сервис заказа товаров для розничных сетей».

## Getting started

At the very first start run `START.sh`. It will build an image, initially fill-in database and start the service.  

To start the service use `docker-compose up -d`. You'll have to wait about 40 seconds before the service is up.  
To stop service use `docker-compose down`.  

Register your first user at `/register`.  
If you need an admin - set your user `"is_admin"` field to true in database manually.

---

1) Install requirements: `pip install -r requirements.txt`
2) Set flask running file: `set FLASK_APP=web_shop/app.py` (for Linux: `export FLASK_APP=web_shop/app.py`)
   2.1) If necessary set flask debugging mode:
      - `set FLASK_DEBUG=1` - to turn debug mode on (for Linux: `export FLASK_DEBUG=1`) 
      - `set FLASK_DEBUG=0` - to turn debug mode off (for Linux: `export FLASK_DEBUG=0`)   
3) Create a new clean database in PostgreSQL 
4) In project root create ".env" with following keys: 
   - DATABASE_URI 
   - SECRET_KEY,
   - SMTP_SERVER,
   - SMTP_NAME,
   - SMTP_USERNAME,
   - SMTP_PASSWORD
   providing that "SMTP" keys shall represent an acting email-service smtp-configuration.
5) Create tables from migrations: `flask db upgrade`
6) Run `python load_db_inits.py`
7) Run `sudo service redis-server`   
8) Run `celery -A web_shop.celery worker`
9) Start app: `flask run` and open `http://127.0.0.1:5000/` in your browser. 

Optional steps:  
10) Register your first user at `/register`
11) If you need an admin - set your user "is_admin" field to true in database manually.  

## Notes

Admin panel is reachable at `/admin` (`is_admin=true` required).
Admin panel link is available from project `/index` view for administrators.

Initial database commits include admin, two sellers, three shops, one customer and a pack of goods.
Seller1 is a manager of Svayznoy and M-Video. Seller2 is a manager of Eldorado. 
You may change their properties in `database/inits.yaml` if you wish, but you shall keep the file schema.

Once the project is running you may use `eldorado.yaml` and/or `svyaznoy.yaml` (from the `web_shop` root) for adding some goods from the personal account of a correspondent seller.
Also, you may create your own YAML with a schema similar to any of the above mentioned two provided files.

It's highly recommended signing in a new customer with an acting email for making orders. 

## Описание

Приложение предназначено для автоматизации закупок в розничной сети. Пользователи сервиса — покупатель (менеджер торговой сети, который закупает товары для продажи в магазине) и поставщик товаров.

**Клиент (покупатель):**

- Менеджер закупок через API делает ежедневные закупки по каталогу, в котором
  представлены товары от нескольких поставщиков.
- В одном заказе можно указать товары от разных поставщиков — это
  повлияет на стоимость доставки.
- Пользователь может авторизироваться, регистрироваться и восстанавливать пароль через API.
    
**Поставщик:**

- Через API информирует сервис об обновлении прайса.
- Может включать и отключать прием заказов.
- Может получать список оформленных заказов (с товарами из его прайса).


### Задача

Необходимо разработать backend-часть (Django) сервиса заказа товаров для розничных сетей.

**Базовая часть:**
[x] Разработка сервиса под готовую спецификацию (API);
[x] Возможность добавления настраиваемых полей (характеристик) товаров;
[x] Импорт товаров;
[x] Отправка накладной на email администратора (для исполнения заказа);
[x] Отправка заказа на email клиента (подтверждение приема заказа).

**Продвинутая часть:**
* Экспорт товаров;
[x] Админка заказов (проставление статуса заказа и уведомление клиента);
[x] Выделение медленных методов в отдельные процессы (email, импорт, экспорт).
