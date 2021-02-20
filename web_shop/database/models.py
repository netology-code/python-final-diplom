"""Database table models."""
import enum
import datetime

import jwt
from flask import jsonify
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from web_shop import app, db, login_manager


class OrderStateChoices(enum.Enum):
    """Order state choices."""

    basket = "Статус корзины"
    new = "Новый"
    confirmed = "Подтвержден"
    assembled = "Собран"
    sent = "Отправлен"
    delivered = "Доставлен"
    canceled = "Отменен"


class UserTypeChoices(enum.Enum):
    """User types choices."""

    shop = "Магазин"
    buyer = "Покупатель"


class User(UserMixin, db.Model):
    """Unified user model."""

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime(), nullable=False)
    is_admin = db.Column(db.Boolean(), default=False)
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime())
    user_type = db.Column(db.Enum(UserTypeChoices), default=UserTypeChoices.buyer, nullable=False)

    # def __init__(self, email: str, is_admin: bool, token: str, expiry: datetime):
    #     self.email = email
    #     self.is_admin = is_admin
    #     self.token = token
    #     self.expires_at = expiry

    def __repr__(self):
        return f"<User {self.username!r} {self.password!r} {self.is_admin!r} {self.expires_at!r}>"

    def set_password(self, password: str) -> None:
        """User password hash setter.

        :param password - raw password string
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """User password hash checker.

        :param password - raw password string
        :return bool
        """
        return check_password_hash(self.password_hash, password)

    def create_checking_token(self):
        """Create a token to send it via email."""
        self.expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=600)
        self.token = jwt.encode({"username": self.email, "exp": self.expires_at}, app.config["SECRET_KEY"])

    @staticmethod
    def check_token(token: str):
        """Check tokens."""
        try:
            # jwt.decode() возвращает словарь с исходными ключами
            # параметр algorithms обязательный
            jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.filter_by(token=token).first()
            if current_user:
                return True
            return False
        except Exception as e:
            return jsonify({"message": e.args[0]}), 401


#
# Shop
# - name
# - url
# - filename
# 2.
# Category
# - shops(m2m)
# - name
# 3.
# Product
# - category
# - name
# 4.
# ProductInfo
# - product
# - shop
# - name
# - quantity
# - price
# - price_rrc
# 5.
# Parameter
# - name
# 6.
# ProductParameter
# - product_info
# - parameter
# - value
# 7.
# Order
# - user
# - dt
# - status
# 8.
# OrderItem
# - order
# - product
# - shop
# - quantity
# 9.
# Contact
# - type
# - user
# - value


@login_manager.user_loader
def load_user(id):
    """Load user from database for login.

    :param id - user id
    :return user string or None
    """
    return User.query.get(int(id))
