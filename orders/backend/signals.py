from django.db.models.signals import pre_delete, post_save
from django.dispatch import Signal, receiver
from django_rest_passwordreset.signals import reset_password_token_created
from social_django.models import UserSocialAuth
from rest_framework.authtoken.models import Token

from backend.models import ConfirmEmailToken, User, ProductInfo
from .tasks import send_email, delete_image

new_user_registered = Signal('user_id')

new_order = Signal('user_id')

update_order = Signal('user_id')

create_image = Signal('user_id')


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """
    Отправляем письмо с токеном для сброса пароля пользователя
    """
    title = f"Password Reset Token for {reset_password_token.user}"
    message = reset_password_token.key
    email = reset_password_token.user.email
    send_email(
        title=title,
        message=message,
        email=email
    )


@receiver(new_user_registered)
def new_user_registered_signal(user_id, **kwargs):
    """
    При регистрации нового пользователя в RegisterAccount
    создает токен подтверждения почты и отправляет
    на почту пользователю
    """
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)
    title = f"Password Reset Token for {token.user.email}"
    message = token.key
    email = token.user.email

    send_email(
        title=title,
        message=message,
        email=email
    )


@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    """
    При подтверждении заказа в OrderView
    отправляет письмо на почту пользователю
    """
    title = f"Обновление статуса заказа"
    message = f'Заказ сформирован'
    email = User.objects.get(id=user_id).email

    send_email(
        title=title,
        message=message,
        email=email
    )


@receiver(update_order)
def update_order_signal(user_id, state, order_id, **kwargs):
    """
    При обновлении статуса заказа в AdminView
    отправляет письмо на почту пользователя с информацией
    о новом статусе заказа
    """
    title = f"Обновление статуса заказа {order_id}"

    message = f'Новый статус заказа: \n{state}'

    email = User.objects.get(id=user_id).email

    send_email(
        title=title,
        message=message,
        email=email
    )


@receiver(pre_delete, sender=ProductInfo)
def product_photo_delete(sender, instance, **kwargs):
    """
    При удалении продукта также
    удаляет файл картинки продукта
    """
    photo = instance.photo
    delete_image(photo)


@receiver(pre_delete, sender=User)
def user_delete(sender, instance, **kwargs):
    """
    При удалении пользователя также
    удаляет файл с картинкой пользователя
    """
    image = instance.image
    delete_image(image)


@receiver(post_save, sender=UserSocialAuth)
def get_token_for_social_user(sender, instance, **kwargs):
    """
    Создает токен для пользователей созданных
    с помощью социальной сетей и отправляет
    письмо с токеном на почту
    """
    if kwargs['created']:
        social_user = instance
        user = User.objects.get(social_auth=social_user)
        token, _ = Token.objects.get_or_create(user=user)

        title = f"Токен для входа в сервис {token.user.email}"
        message = token.key
        email = token.user.email

        send_email(
            title=title,
            message=message,
            email=email
        )
