from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator as token_generator


def send_email_4_verification(request, user):
    current_site = get_current_site(request)
    context = {
        # "email": user_email,
        "domain": current_site.domain,
        # "site_name": site_name,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "user": user,
        "token": token_generator.make_token(user),
        # "protocol": "https" if use_https else "http",
        # **(extra_email_context or {}),
    }
    # message = render_to_string()
    message = "Подтверди уже пароль, млять!"
    email = EmailMessage(
        'Verify eail',
        message,
        to=[user.email]
    )
    email.send()
