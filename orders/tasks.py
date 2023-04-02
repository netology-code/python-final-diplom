# import random
from celery import shared_task
# from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage


# from rest_framework.authtoken.models import Token

# app = celery.Celery(broker='redis://127.0.0.1:6379/1',
#                     backend='redis://127.0.0.1:6379/2')


@shared_task(serializer='json')
def send_email_4_verification(current_site: str,
                              user_email: str,
                              token: str) -> None:
    message = f"Please follow this link to confirm your password: \n " \
              f"http://{current_site}/api/v1/user/verify_email/" \
              f"{token}"
    email = EmailMessage(
        'Verify email',
        message,
        to=[user_email],
    )
    email.send()


@shared_task(serializer='json')
def send_email_4_reset_passw(user, token):
    # token, _ = Token.objects.get_or_create(user=user)
    # message = f"Please use this token for you request : \n " \
    #           f"{token}"
    # email = EmailMessage(
    #     'reset_password',
    #     message,
    #     to=[user.email],
    # )
    # email.send()
    pass

#
# @shared_task
# def add(x, y):
#     # Celery recognizes this as the `movies.tasks.add` task
#     # the name is purposefully omitted here.
#     return x + y
#
#
# @shared_task(name="multiply_two_numbers")
# def mul(x, y):
#     # Celery recognizes this as the `multiple_two_numbers` task
#     total = x * (y * random.randint(3, 100))
#     return total
#
#
# @shared_task(name="sum_list_numbers")
# def xsum(numbers):
#     # Celery recognizes this as the `sum_list_numbers` task
#     return sum(numbers)
