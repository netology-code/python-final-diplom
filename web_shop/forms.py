"""Forms for rendering html templates."""

from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo

from web_shop.database import User


class MyLoginForm(FlaskForm):
    """Web form for login template."""

    email = StringField("Адрес электронной почты", validators=[DataRequired(message="Адрес не указан")])
    password = PasswordField("Пароль учётной записи", validators=[DataRequired(message="Пароль не указан")])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")
    retrieve_password = SubmitField("Восстановить пароль")


class MyRegisterForm(FlaskForm):
    """Form for registration template."""

    first_name = StringField("Имя", validators=[DataRequired(message="Имя не указано")])
    last_name = StringField("Фамилия", validators=[DataRequired(message="Фамилия не указана")])
    email = StringField("Адрес электронной почты", validators=[DataRequired(message="Адрес не указан")])
    password = PasswordField("Пароль учётной записи", validators=[DataRequired(message="Пароль не указан")])
    password_confirm = PasswordField(
        "Повторите пароль",
        validators=[
            DataRequired(message="Пароль не указан"),
            EqualTo(fieldname=password, message="Пароли не совпадают"),
        ],
    )
    submit = SubmitField("Зарегистрироваться")

    def validate_email(self, email):
        """Email validator."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")


class MyResetPasswordForm(FlaskForm):
    """Form for password reset template."""

    pass


class MyForgotPasswordForm(FlaskForm):
    """Form for forgotten password template."""

    pass


class MyChangePasswordForm(FlaskForm):
    """Form for password change template."""

    pass
