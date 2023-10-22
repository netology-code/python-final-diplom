#### _the diploma was developed by Oleg Sungurovsky <safasgasc.asfg@gmail.com>_

## Description

The application is designed to automate a retail procurement. A Buyer (a manager of trading network who purchases goods
to be sold in a shop) and a Supplier of the goods are users of the service.

**Opportunities of a client:**

- Using API a purchasing manager makes the purchases from the catalogue where goods from different suppliers are
  presented.
- Goods from different suppliers may be chosen. This influences on cost of the delivery.
- A User is able to log in register and recover the password via API.

**Opportunities of a supplier:**

- Informs the service about an updating of price via API.
- Can turn on and off taking orders.
- Can receive a list of clearance of goods (with goods from goods price list).

The following technologies are involved In the project:

* Python 3
* Django
* Django Rest Framework
* Django Versatile Image Field
* Django baton (custom admin panel)
* DRF-yasg (Yet another Swagger generator)
* Celery
* Redis server
* Social Auth

## Installation of the apps via Docker-Compose

1. Create a GitHub app and Mail.ru:
   - [Creating the GitHub App](https://github.com/settings/applications/new)
   - [Creating the Mail.ru App](https://oauth.mail.ru/app/)
2. Configure Django to send mail:
   - [Instruction](https://vivazzi.pro/ru/it/send-email-in-django/)
3. Create **.env.dev** file with the following fields and fill them in:

```
SECRET_KEY=<django secret key>
DEBUG=<django debug(True or False)>
ALLOWED_HOSTS=<[is list having addresses of all domains which can run your Django Project]>

Database Settings
ENGINE=<databse engin(default: postgres)>
NAME=<database name>
PORT=<database port(default: 5432)>
HOST=<database host(with docker: db; without docker: 127.0.0.1)>
USER=<database user>
PASSWORD=<database user's password>
DATABASE=<postgres>

Settings send email
EMAIL_HOST=< >
EMAIL_HOST_USER=< >
EMAIL_HOST_PASSWORD=< >
EMAIL_PORT=< >
EMAIL_USE_TLS=< >
or
EMAIL_USE_SSL=< >

Settings Celery
CELERY_BROKER_URL=<default: redis://redis:6379/0>
CELERY_BROKER_TRANSPORT=<default: redis>
CELERY_RESULT_BACKEND=<default: django-db>

Database settings for Docker-compose
POSTGRES_USER=<USER>
POSTGRES_PASSWORD=<PASSWORD>
POSTGRES_DB=<NAME>

Apps settings for Social Auth
SOCIAL_AUTH_GITHUB_KEY=<key of github app>
SOCIAL_AUTH_GITHUB_SECRET=<secret of github app>

SOCIAL_AUTH_MAILRU_KEY=<key of mail.ru app>
SOCIAL_AUTH_MAILRU_SECRET=<secret of mail.ru app>
```

4. It is necessary to install a docker on PC
5. For using Google Analytics:
   *  Add the file```credentials.json``` ([Instruction](https://support.google.com/a/answer/7378726))
   * [Create](https://developers.google.com/analytics/learn?hl=ru) Google Analytics account
   * Add the variable ```ANALYTICS_VIEW_ID=<the view id of your google analytic>``` in ```.env.dev```

If you don't want to use  Google Analytics delete the following code block from [settings.py](orders%2Fsettings.py) into setting ```Baton```:
```
'ANALYTICS': {
     'CREDENTIALS': os.path.join(BASE_DIR, 'credentials.json'),
     'VIEW_ID': os.environ.get('ANALYTICS_VIEW_ID', default='11111'),
 }
```
   
6. Use the commands below build and launch the app


```bash
docker-compose build
```

```bash
docker-compose up -d
```

## The local installation without a Docker

Clone the repository with the help of git

    git clone https://github.com/OlegSungyrovsky/python-final-diplom

Go to the folder:

```bash
cd orders
```

Create and activate virtual environment Python.

```bash
python3 -m venv env 
```

Install the packages from  **requirements.txt**:

```bash
pip install -r requirements.txt
```

The commands for a creation of migrations for the database

```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

## Creation of the Superuser

```bash
python manage.py createsuperuser
```

Enter the email and password. Authorisation in the admin panel after launching of the application is
at: http://127.0.0.1:8000/admin/

Command for the launching of the Application

```bash
python manage.py runserver
```

The Application will be available at: http://127.0.0.1:8000/

## API is also published on server POSTMAN:

[Postman documentation](https://documenter.getpostman.com/view/24872439/2s9YJez1xd)