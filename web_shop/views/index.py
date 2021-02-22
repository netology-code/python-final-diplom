"""Index views for login, logout and registration."""
from datetime import datetime, timedelta

from flask import Response, flash, make_response, redirect, render_template, request, url_for
from flask_admin import AdminIndexView
from flask_jwt_extended import create_access_token, jwt_required
from flask_login import current_user, login_user, logout_user
from itsdangerous import BadPayload, BadSignature, SignatureExpired

from web_shop import app, db, mail, token_serializer
from web_shop.database.models import User, UserTypeChoices
from web_shop.emails.mail_sender import create_confirmation_token, create_message
from web_shop.forms import MyLoginForm, MyRegisterForm


@app.route("/")
# @jwt_required(locations=['cookies'])
def index():
    """Index view."""
    print(request.cookies)
    return render_template("base.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login route handler."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = MyLoginForm()
    if form.is_submitted():
        if not form.email.data and not form.password.data:
            flash("Адрес и пароль не указаны")
            return make_response(redirect(url_for("login")))

        if not form.email.data:
            flash("Адрес не указан")
            return make_response(redirect(url_for("login")))

        if not form.password.data:
            flash("Пароль не указан")
            return make_response(redirect(url_for("login")))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash("Пользователь не зарегистрирован")
            return make_response(redirect(url_for("login")))

        if not user.check_password(form.password.data):
            flash("Ошибка при вводе адреса почты или пароля")
            return make_response(redirect(url_for("login")))
        login_user(user, remember=form.remember_me.data)

        if not user.confirmed_at:
            flash("Проверьте почту и активируйте учётную запись")
            return redirect(url_for("index"))

        if request.args.get("next"):
            resp: Response = make_response(redirect(url_for(request.args.get("next"))))
        else:
            resp: Response = make_response(redirect(url_for("index")))
        token = create_access_token(identity=user.email, expires_delta=timedelta(seconds=30))
        resp.set_cookie("access_token_cookie", token)
        return resp

    return make_response(render_template("login.html", title="Вход в учётную запись", form=form))


@app.route("/logout")
def logout():
    """Logout user route handler."""
    logout_user()
    return make_response(redirect(url_for("index")))


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration route handler."""
    if current_user.is_authenticated:
        return make_response(redirect(url_for("index")))

    form = MyRegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data)
        user.set_password(form.password.data)
        user.user_type = getattr(UserTypeChoices, form.user_type.data).name
        db.session.add(user)
        db.session.commit()

        token = create_confirmation_token(user.email)
        message = create_message(user.email, token)
        mail.send(message)
        flash("Регистрация прошла успешно! Проверьте вашу почту и подтвердите учётную запись в течение 1 минуты.")
        return make_response(redirect(url_for("index")))

    return make_response(render_template("register.html", title="Регистрация", form=form))


@app.route("/confirm/<token>")
def confirm_email(token):
    """Confirm email after registration."""
    email = token_serializer.loads(token, salt=app.config["SECRET_KEY"])
    user = User.query.filter_by(email=email).first()
    if user:
        try:
            token_serializer.loads(token, salt=app.config["SECRET_KEY"], max_age=60)
            user.confirmed_at = datetime.now()
            db.session.commit()
            flash("Учётная запись подтверждена")
            return make_response(redirect(url_for("login")))
        except (BadPayload, BadSignature, SignatureExpired):
            if user.confirmed_at:
                return make_response(redirect(url_for("login")))
            db.session.delete(user)
            db.session.commit()
    flash("Ссылка больше недействительна. Пройдите регистрацию заново.")
    return make_response(redirect(url_for("register")))


class MyAdminIndexView(AdminIndexView):
    """Overrides access to admin index page."""

    def is_accessible(self):
        """Lets user enter admin view on condition."""
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        """Redirects user to login view on admin view entering if user is not logged in."""
        # redirect to login page if user doesn't have access
        return make_response(redirect(url_for("login", next="admin.index")))
