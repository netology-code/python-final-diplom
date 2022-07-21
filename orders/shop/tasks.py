import requests
from django.db import IntegrityError
from yaml import load as load_yaml, Loader
from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from orders.celery import app
from .models import Category, Parameter, ProductParameter, Product, Shop, ProductInfo


@app.task()
def send_email(message: str, email: str, *args, **kwargs):
    title = "Title"
    email_list = []
    email_list.append(email)
    try:
        msg = EmailMultiAlternatives(subject=title, body=message, from_email=EMAIL_HOST_USER, to=email_list)
        msg.send()
        return f'Title: {msg.subject}, Message: {msg.body}'
    except Exception as e:
        raise e


@app.task()
def import_shop_data(partner, url):
    if url:
        validate_url = URLValidator()
        try:
            validate_url(url)
        except ValidationError as e:
            return {'Status': False, 'Error': str(e)}
        else:
            stream = requests.get(url).content
            data = load_yaml(stream, Loader)

            try:
                shop, _ = Shop.objects.get_or_create(user_id=partner, name=data['shop'])
            except IntegrityError as e:
                return {'Status': False, 'Error': str(e)}

            for category in data['categories']:
                category_object, _ = Category.objects.get_or_create(
                    id=category['id'],
                    name=category['name']
                )
                category_object.shops.add(shop.id)
                category_object.save()

            ProductInfo.objects.filter(shop_id=shop.id).delete()

            for item in data['goods']:
                product, _ = Product.objects.get_or_create(
                    name=item['name'],
                    category_id=item['category']
                )
                product_info = ProductInfo.objects.create(
                    product_id=product.id,
                    article=item['id'],
                    model=item['model'],
                    price=item['price'],
                    price_rrc=item['price_rrc'],
                    quantity=item['quantity'],
                    shop_id=shop.id
                )

                for name, value in item['parameters'].items():
                    parameter, _ = Parameter.objects.get_or_create(name=name)
                    ProductParameter.objects.create(
                        product_info_id=product_info.id,
                        parameter_id=parameter.id,
                        value=value
                    )

            return {'Status': True}
    return {'Status': False, 'Errors': 'Url is false'}
