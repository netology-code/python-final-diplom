"""A profound email validator."""
import re

from wtforms import ValidationError

from web_shop.database import User


class MyValidator(object):
    """Parent class with parent methods.

    :param message: Error message to raise in case of a validation error.
    """

    def __init__(self, message: str = None):
        self.message = message

    def __call__(self, form, field):
        try:
            if field.data is None:
                raise ValueError()
            return self.validate(field.data)
        except ValueError as e:
            raise ValidationError(e.args[0])

    def validate(self, arg):
        """Starts validation."""
        pass

    @staticmethod
    def check_ascii(string: str) -> bool:
        """All symbols must be ASCII."""
        if string.isascii():
            return True
        raise ValueError("Буквы могут быть только латинскими")

    @staticmethod
    def check_len(string: str, key: str) -> bool:
        if key == "email":
            """Name length must be 4 or greater."""
            if len(string.split("@")[0]) >= 4:
                return True
            raise ValueError(
                'Длина имени адреса до символа "@" не может быть меньше 4 символов'
            )
        if key == "pass":
            """Password length must be 4 or greater."""
            if 8 <= len(string) <= 14:
                return True
            raise ValueError("Длина пароля должна быть не менее 8 и не более 14 символов")


class MyEmailValidator(MyValidator):
    """Validates an email address."""

    def validate(self, email):
        """Starts email validation."""
        user = User.query.filter_by(email=email).first()
        if user is not None:
            raise ValueError("Данный адрес электронной почты уже используется")

        try:
            if all(
                (
                    self.check_ascii(email),
                    self.check_prohibited(email),
                    self.check_len(email, "email"),
                    self.check_at_symbol(email),
                    self.check_domain_len(email),
                    self.check_domain_zone_len(email),
                )
            ):
                return True
        except ValueError as e:
            raise ValueError(e.args[0])

    @staticmethod
    def check_domain_zone_len(email: str) -> bool:
        """Domain zone length must be in range(2,4) inclusive."""
        if 2 <= len(email.rsplit(".", 1)[-1]) <= 4:
            return True
        raise ValueError(
            "Длина доменной зоны должна быть не менее 2 и не более 4 символов"
        )

    @staticmethod
    def check_domain_len(email: str) -> bool:
        """Domain length must be 2 or greater."""
        if len(email.split("@")[-1].rsplit(".", 1)[0]) >= 2:
            return True
        raise ValueError("Длина доменного имени должна быть не менее 2 символов")

    @staticmethod
    def check_at_symbol(email: str) -> bool:
        """@ count must be equal 1 sharp."""
        if "@" in email:
            if email.count("@") == 1:
                return True
            raise ValueError('В адресе почты может быть только один символ "@"')
        raise ValueError('В адресе почты должен быть один символ "@"')

    @staticmethod
    def check_prohibited(email: str) -> bool:
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
        if all(i not in email for i in prohibited_symbols):
            return True
        raise ValueError("Недопустимые знаки препинания в адресе почты")


class MyPasswordValidator(MyValidator):
    """Validates a password string."""

    def validate(self, password):
        """Starts validation."""
        try:
            if all(
                (
                    self.check_letters(password),
                    self.check_len(password, "pass"),
                    self.check_ascii(password),
                    self.check_nums(password),
                    self.check_punctuation(password),
                    self.check_case(password),
                )
            ):
                return True
        except ValueError as e:
            raise ValueError(e.args[0])

    @staticmethod
    def check_nums(password: str) -> bool:
        """Check if numbers are in password."""
        if re.findall(r"\d", password):
            return True
        raise ValueError("Пароль должен содержать хотя бы одну цифру")

    @staticmethod
    def check_letters(password: str) -> bool:
        """Check if letters are in password."""
        from unicodedata import category

        if any(category(i).startswith("L") for i in password):
            return True
        raise ValueError("Пароль должен содержать хотя бы две буквы")

    @staticmethod
    def check_punctuation(password: str) -> bool:
        """Check if punctuation signs are in password."""
        if re.findall(r"\W|_", password):
            return True
        raise ValueError("Пароль должен содержать хотя бы один знак препинания")

    @staticmethod
    def check_case(password: str) -> bool:
        """Check if letters of different case are in password."""
        if password != password.upper() and password != password.lower():
            return True
        raise ValueError("Пароль должен содержать буквы в разных регистрах")
