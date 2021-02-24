"""A profound email validator."""

from wtforms import ValidationError


class MyEmailValidator(object):
    """Validates an email address.

    :param message: Error message to raise in case of a validation error.
    """

    def __init__(self, message: str = None):
        self.message = message

    def __call__(self, form, field):
        try:
            if field.data is None:
                raise ValueError()
            return self.validate_email(field.data)
        except ValueError:
            message = self.message
            if not message:
                message = field.gettext("Invalid email address.")
            raise ValidationError(message)

    @staticmethod
    def validate_email(email):
        """Starts validation."""
        if not all(
            (
                check_ascii(email),
                check_domain_len(email),
                check_name_len(email),
                check_domain_zone_len(email),
                check_prohibited(email),
            )
        ):
            raise ValueError
        return True


def check_prohibited(email) -> bool:
    """No prohibited symbols in email."""
    prohibited_symbols = [
        " ",
        ",",
        ":",
        ";",
        "!",
        "#",
        "%",
        "*",
        "(",
        ")",
        "=",
        "+",
        "{",
        "}",
        "[",
        "]",
        '"',
        "'",
        "/",
        "\\",
        "|",
    ]
    return all(i not in email for i in prohibited_symbols)


def check_ascii(email) -> bool:
    """All symbols must be ASCII."""
    return email.isascii()


def check_name_len(email) -> bool:
    """Name length must be 4 or greater."""
    return len(email.split("@")[0]) >= 4


def check_domain_zone_len(email) -> bool:
    """Domain zone length must be in range(2,4) inclusive."""
    return 2 <= len(email.rsplit(".", 1)[-1]) <= 4


def check_domain_len(email) -> bool:
    """Domain length must be 2 or greater."""
    return len(email.split("@")[-1].rsplit(".", 1)[0]) >= 2
