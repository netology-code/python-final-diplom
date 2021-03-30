"""Email creating module."""
from flask_mail import Message

from web_shop import app, celery, mail, token_serializer


def create_confirmation_token(obj):
    """Create confirmation token to be sent via email after registration."""
    return token_serializer.dumps(obj, salt=app.config["SECRET_KEY"])


def create_message(subject: str, addresses: str or list or tuple):
    """Create a message to be sent via email."""
    if isinstance(addresses, (list, tuple)):
        recipients = addresses
    elif isinstance(addresses, str):
        recipients = [addresses]
    else:
        raise ValueError(
            "Recipients' addresses must be tuple or list of strings (if many) or str (if one)"
        )

    return Message(subject, recipients=recipients, sender=app.config["MAIL_USERNAME"])


@celery.task()
def send_message(message: Message):
    """Send message via email as a celery-task."""
    with app.app_context():
        mail.send(message)
