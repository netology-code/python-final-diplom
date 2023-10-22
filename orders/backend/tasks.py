from celery import shared_task
from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail.message import EmailMultiAlternatives
from requests import get
from versatileimagefield.fields import VersatileImageField
from yaml import Loader
from yaml import load as load_yaml

from .models import Category, Parameter, Product, ProductInfo, ProductParameter, Shop


@shared_task()
def send_email(title, message, email, *args, **kwargs):
    """
    Отправляет письмо на заданный email
    :param title: Заголовок письма
    :param message: текст письма
    :param email: Адрес почты на которую будет оправлено письмо
    :param args: args
    :param kwargs: kwargs
    :return: None
    """
    msg = EmailMultiAlternatives(
        subject=title,
        body=message,
        from_email=EMAIL_HOST_USER,
        to=[email]
    )
    msg.send()


@shared_task()
def do_import(url, user_id, *args, **kwargs):
    """
    Импортирует товары с помощью ссылки на yaml файл
    :param url: ссылка на yaml файл с продуктами поставщика
    :param user_id: Id пользователя магазина
    :param args: args
    :param kwargs: kwargs
    :return: True or False
    """
    stream = get(url).content
    try:
        data = load_yaml(stream=stream, Loader=Loader)
        shop = data['shop']
        categories = data['categories']
        goods = data['goods']

    except Exception as err:
        return False
    shop, _ = Shop.objects.get_or_create(name=shop, user_id=user_id)
    for category in categories:
        category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
        category_object.shops.add(shop.id)
        category_object.save()
    ProductInfo.objects.filter(shop_id=shop.id).delete()
    for item in goods:
        product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

        product_info = ProductInfo.objects.create(product_id=product.id,
                                                  external_id=item['id'],
                                                  model=item['model'],
                                                  price=item['price'],
                                                  price_rrc=item['price_rrc'],
                                                  quantity=item['quantity'],
                                                  shop_id=shop.id)

        for name, value in item['parameters'].items():
            parameter_object, _ = Parameter.objects.get_or_create(name=name)
            ProductParameter.objects.create(product_info_id=product_info.id,
                                            parameter_id=parameter_object.id,
                                            value=value)
    return True


@shared_task()
def delete_image(image: VersatileImageField, *args, **kwargs):
    """
    Удаляет файл картинки из приложения, если она не default
    :param image: картинка (VersatileImageField) для удаления
    :param args: args
    :param kwargs: kwargs
    :return: None
    """

    default_image_user = 'default_image.png'
    default_image_product = 'default_product_image.jpg'
    image_name = str(image).split('/')[-1]

    if image_name != default_image_user and image_name != default_image_product:
        image.delete_all_created_images()
        image.delete(False)

