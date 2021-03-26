"""Forms for rendering html templates."""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, EqualTo

from web_shop.database import UserTypeChoices
from web_shop.validators.validators import MyEmailValidator, MyPasswordValidator


class MyLoginForm(FlaskForm):
    """Web form for login template."""

    email = StringField(
        "Адрес электронной почты", validators=[DataRequired(message="Адрес не указан")],
    )
    password = PasswordField(
        "Пароль учётной записи", validators=[DataRequired(message="Пароль не указан")],
    )
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class MyRegisterForm(FlaskForm):
    """Form for registration template."""

    first_name = StringField("Имя", validators=[DataRequired(message="Имя не указано")])
    last_name = StringField(
        "Фамилия", validators=[DataRequired(message="Фамилия не указана")]
    )
    email = StringField(
        "Адрес электронной почты",
        validators=[DataRequired(message="Адрес не указан"), MyEmailValidator()],
    )
    password = PasswordField(
        "Пароль учётной записи",
        validators=[
            DataRequired(message="Пароль не указан"),
            MyPasswordValidator(),
            EqualTo(fieldname="password_confirm", message="Пароли не совпадают"),
        ],
    )
    password_confirm = PasswordField(
        "Повторите пароль",
        validators=[
            DataRequired(message="Пароль не указан"),
            EqualTo(fieldname="password", message="Пароли не совпадают"),
        ],
    )
    user_type = SelectField(
        "Тип пользователя",
        choices=[
            (UserTypeChoices.customer.name, UserTypeChoices.customer.value),
            (UserTypeChoices.seller.name, UserTypeChoices.seller.value),
        ],
        coerce=str,
        validators=[DataRequired()],
    )
    submit = SubmitField("Зарегистрироваться")
    cancel = SubmitField("Отмена")


class MyResetPasswordForm(FlaskForm):
    """Form for password reset template."""

    email = StringField(
        "Адрес электронной почты", validators=[DataRequired(message="Адрес не указан")],
    )
    submit = SubmitField("Отправить")


class MyForgotPasswordForm(MyResetPasswordForm):
    """Form for forgotten password template."""

    pass


class MyForm(FlaskForm):
    """Buttons in change-forms."""

    submit = SubmitField("Сохранить")
    cancel = SubmitField("Отмена")


class MyNameChangeForm(MyForm):
    """Name change form."""

    first_name = StringField("Имя")
    last_name = StringField("Фамилия")


class MyEmailChangeForm(MyForm):
    """Email change form."""

    email = StringField(
        "Адрес электронной почты",
        validators=[DataRequired(message="Адрес не указан"), MyEmailValidator()],
    )


class MyPasswordChangeForm(MyForm):
    """Password change form."""

    password = PasswordField(
        "Пароль учётной записи",
        validators=[
            DataRequired(message="Пароль не указан"),
            MyPasswordValidator(),
            EqualTo(fieldname="password_confirm", message="Пароли не совпадают"),
        ],
    )
    password_confirm = PasswordField(
        "Повторите пароль",
        validators=[
            DataRequired(message="Пароль не указан"),
            EqualTo(fieldname="password", message="Пароли не совпадают"),
        ],
    )
