from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created

from .models import ConfirmEmailToken, User
from .tasks import send_email

new_user_registered = Signal('user_id')

new_order = Signal('user_id')

update_order = Signal('user_id')


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """
    Отправляем письмо с токеном для сброса пароля
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param kwargs:
    :return:
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
    title = f"Обновление статуса заказа {order_id}"

    message = f'Новый статус заказа: \n{state}'

    email = User.objects.get(id=user_id).email

    send_email(
        title=title,
        message=message,
        email=email
    )
