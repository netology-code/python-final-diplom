"""Forms for rendering html templates."""

from flask_wtf import FlaskForm

from wtforms import SelectField, StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

from web_shop.validators.email import MyEmailValidator
from web_shop.database import User, UserTypeChoices


class MyLoginForm(FlaskForm):
    """Web form for login template."""

    email = StringField("Адрес электронной почты", validators=[DataRequired(message="Адрес не указан")])
    password = PasswordField("Пароль учётной записи", validators=[DataRequired(message="Пароль не указан")])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class MyRegisterForm(FlaskForm):
    """Form for registration template."""

    first_name = StringField("Имя", validators=[DataRequired(message="Имя не указано")])
    last_name = StringField("Фамилия", validators=[DataRequired(message="Фамилия не указана")])
    email = StringField(
        "Адрес электронной почты",
        validators=[
            DataRequired(message="Адрес не указан"),
            Email(message="Введите адрес электронной почты"),
            MyEmailValidator("Введите адрес электронной почты"),
        ],
    )
    password = PasswordField(
        "Пароль учётной записи",
        validators=[
            DataRequired(message="Пароль не указан"),
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
            (UserTypeChoices.buyer.name, UserTypeChoices.buyer.value),
            (UserTypeChoices.shop.name, UserTypeChoices.shop.value),
        ],
        # choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')],
        coerce=str,
        validators=[DataRequired()],
    )
    submit = SubmitField("Зарегистрироваться")

    def validate_email(self, email):  # INFO: do not turn into static method
        """Email validator."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Данный адрес электронной почты уже используется")


class MyResetPasswordForm(FlaskForm):
    """Form for password reset template."""

    pass


class MyForgotPasswordForm(FlaskForm):
    """Form for forgotten password template."""

    pass


class MyChangePasswordForm(FlaskForm):
    """Form for password change template."""

    pass
