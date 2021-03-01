"""Database table models."""
import enum
from datetime import datetime, timedelta, timezone

import jwt
from flask import jsonify
from flask_login import UserMixin
from sqlalchemy.orm import backref, relationship
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

    __table_args__ = {"extend_existing": True}
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean(), default=False)
    is_active = db.Column(db.Boolean(), default=False)
    confirmed_at = db.Column(db.DateTime())
    user_type = db.Column(db.Enum(UserTypeChoices), default=UserTypeChoices.buyer, nullable=False)

    def set_password(self, password: str) -> None:
        """User password hash setter.

        :param password - raw password string
        """
        self.password = generate_password_hash(password)
        return self.password

    def check_password(self, password: str) -> bool:
        """User password hash checker.

        :param password - raw password string
        :return bool
        """
        return check_password_hash(self.password, password)

    # def create_access_token(self):
    #     """Create a token to send it via email."""
    #     expires_at = datetime.utcnow() + timedelta(seconds=10)
    #     return jwt.encode({"username": self.email, "exp": expires_at}, app.config["SECRET_KEY"])
    #
    # @staticmethod
    # def check_access_token(token: str):
    #     """Check tokens."""
    #     try:
    #         # jwt.decode() возвращает словарь с исходными ключами
    #         # параметр algorithms обязательный
    #         jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    #         current_user = User.query.filter_by(token=token).first()
    #         if current_user:
    #             return True
    #         return False
    #     except Exception as e:
    #         return jsonify({"message": e.args[0]}), 401


# class Shop(db.Model):
#     __tablename__ = "shop"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False, unique=True)
#     url = db.Column(db.String(255), nullable=True, unique=True)
#     filename = db.Column(db.String(255), nullable=True, unique=True)
#
#
# class Category(db.Model):
#     __tablename__ = "category"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False, name="Название")
#
#
# class Product(db.Model):
#     __tablename__ = "product"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False, unique=True)
#     category = db.Column(db.Integer(), db.ForeignKey("category.id"), nullable=False)
#
#
# class ProductInfo(db.Model):
#     __tablename__ = "product_info"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False, unique=True)
#     product = db.Column(db.Integer(), db.ForeignKey("product.id"), nullable=False)
#     shop = db.Column(db.Integer(), db.ForeignKey("shop.id"), nullable=False)
#     price = db.Column(db.Integer(), nullable=False)
#     quantity = db.Column(db.Integer(), nullable=False)
#     # - price_rrc
#
#
# class Parameter(db.Model):
#     __tablename__ = "parameter"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False, unique=True)
#
#
# class ProductParameter(db.Model):
#     __tablename__ = "x_product_parameter"
#     product_info = db.Column(db.Integer(), db.ForeignKey("product_info.id"), primary_key=True, nullable=False)
#     parameter = db.Column(db.Integer(), db.ForeignKey("parameter.id"), primary_key=True, nullable=False)
#     value = name = db.Column(db.String(255), nullable=False)
#
#
# class Order(db.Model):
#     user = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
#
#
# # - dt
# # - status
#
# # 8.
# # OrderItem
# # - order
# # - product
# # - shop
# # - quantity
#
# # 9.
# # Contact
# # - type
# # - user
# - value


@login_manager.user_loader
def load_user(id):
    """Load user from database for login.

    :param id - user id
    :return user string or None
    """
    return User.query.get(int(id))
