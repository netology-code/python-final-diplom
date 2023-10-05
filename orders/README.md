#### _the diploma was developed by Oleg Sungurovsky <safasgasc.asfg@gmail.com>_ 

## Description

The application is designed to automate a retail procurement. A Buyer (a manager of trading network who purchases goods to be sold in a shop) and a Supplier of the goods are users of the service.

**Opportunities of a client:**

- Using API a purchasing manager makes the purchases from the catalogue where goods from different suppliers are presented.
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
* Celery
* Redis server


## Installation of the apps via Docker-Compose
1. Create **.env.dev** file with the following fields and fill them in:
```
SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=
ENGINE=
NAME=
PORT=
HOST=
USER=
PASSWORD=
DATABASE=
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_PORT=
EMAIL_USE_TLS=
PGDATA=
CELERY_BROKER_URL=
CELERY_BROKER_TRANSPORT=
CELERY_RESULT_BACKEND=
```

2. It is necessary to install a docker on PC
3. Use the commands below build and launch the app
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
Enter the email and password. Authorisation in the admin panel after launching of the application is at: http://127.0.0.1:8000/admin/

Command for the launching of the Application
```bash
python manage.py runserver
```
The Application will be available at: http://127.0.0.1:8000/

## API is also published on server POSTMAN:

[Postman documentation](https://documenter.getpostman.com/view/24872439/2s9YJez1xd)