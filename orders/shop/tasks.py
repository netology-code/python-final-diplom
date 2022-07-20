import yaml
from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail.message import EmailMultiAlternatives
from orders.celery import app
from .models import Category, Parameter, ProductParameter, Product, Shop


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


def open_file(shop):
    with open(shop.get_file(), 'r') as f:
        data = yaml.safe_load(f)
    return data


def import_shop_data(data, user_id):
    file = open_file(data)

    shop, _ = Shop.objects.get_or_create(user_id=user_id, defaults={'name': file['shop']})

    load_category = [Category(id=category['id'], name=category['name']) for category in file['categories']]
    Category.objects.bulk_create(load_category)
    Product.objects.filter(shop_id=shop.id).delete()

    load_product = []
    product_id = []
    load_pp = []

    for item in file['goods']:
        load_product.append(Product(
            name=item['name'],
            category_id=item['category'],
            model=item['item'],
            external_id=item['id'],
            shop_id=shop.id,
            quantity=item['quantity'],
            price=item['price'],
            price_rrc=item['price_rrc']
        ))
        product_id[item['id']] = {}

        for name, value in item['parameters'].items():
            parameter, _ = Parameter.objects.get_or_create(name=name)
            product_id[item['id']].update({parameter.id: value})
            load_pp.append(ProductParameter(
                product_id=product_id[item['id']][parameter.id],
                parameter_id=parameter.id,
                value=value
            ))

    Product.objects.bulk_create(load_product)
    ProductParameter.objects.bulk_create(load_pp)
