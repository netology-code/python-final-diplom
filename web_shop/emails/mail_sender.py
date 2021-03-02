"""Email creating module."""

from flask_mail import Message

from web_shop import app, celery, mail, token_serializer


def create_confirmation_token(obj):
    """Create confirmation token to be sent via email after registration."""
    return token_serializer.dumps(obj, salt=app.config["SECRET_KEY"])


def create_message(topic, recipients_addresses):
    """Create a message to be sent via email."""
    return Message(topic, recipients=[recipients_addresses], sender=app.config["MAIL_NAME"])


@celery.task
def send_message(message):
    """Send message via email as a celery-task."""
    with app.app_context():
        mail.send(message)
