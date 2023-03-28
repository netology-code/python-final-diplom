import celery
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from rest_framework.authtoken.models import Token

app = celery.Celery(broker='redis://127.0.0.1:6379/1',
                    backend='redis://127.0.0.1:6379/2')


@app.task()
def send_email_4_verification(request, user):
    current_site = get_current_site(request)
    token, _ = Token.objects.get_or_create(user=user)
    message = f"Please follow this link to confirm your password: \n " \
              f"http://{current_site.domain}/api/v1/user/verify_email/" \
              f"{token}"
    email = EmailMessage(
        'Verify email',
        message,
        to=[user.email],
    )
    email.send()


@app.task()
def send_email_4_reset_passw(user, token):
    token, _ = Token.objects.get_or_create(user=user)
    message = f"Please use this token for you request : \n " \
              f"{token}"
    email = EmailMessage(
        'reset_password',
        message,
        to=[user.email],
    )
    email.send()
