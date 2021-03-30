"""Database table models."""
import enum

from flask_login import UserMixin
from slugify import slugify
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from web_shop import db, login_manager

__all__ = [
    "Category",
    "OrderStateChoices",
    "Shop",
    "Product",
    "ProductParameter",
    "Parameter",
    "ProductInfo",
    "User",
    "UserTypeChoices",
    "load_user",
]


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

    seller = "Продавец"
    customer = "Покупатель"


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
    user_type = db.Column(
        db.Enum(UserTypeChoices), default=UserTypeChoices.customer, nullable=False,
    )

    def __init__(
        self,
        email,
        password,
        first_name,
        last_name,
        id=None,
        is_admin=False,
        is_active=False,
        confirmed_at=None,
        user_type="customer",
    ):
        self.id = id
        self.email = email
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin
        self.is_active = is_active
        self.confirmed_at = confirmed_at
        self.user_type = user_type

    def __str__(self):
        return self.email

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


class Shop(db.Model):
    """Shop table model."""

    __tablename__ = "shop"
    # __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    url = db.Column(db.String(255), nullable=True, unique=True)
    filename = db.Column(db.String(255), nullable=True, unique=True)
    file_upload_datetime = db.Column(db.DateTime(), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    shop_manager = relationship("User")

    def __init__(
        self, title, user_id, id=None, url=None, filename=None, file_upload_datetime=None
    ):
        self.id = id
        self.title = title
        self.url = url
        self.filename = filename
        self.file_upload_datetime = file_upload_datetime
        self.user_id = user_id

    def __repr__(self):
        return self.title


class Category(db.Model):
    """Category table model."""

    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, name="Название")

    def __init__(self, name, id=None):
        self.id = id
        self.name = name


class Product(db.Model):
    """Product table model."""

    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    category = db.Column(db.Integer(), db.ForeignKey("category.id"), nullable=False)

    def __init__(self, name, category, id=None):
        self.id = id
        self.name = name
        self.category = self.__set_category(category)

    @staticmethod
    def __set_category(name: str) -> int:
        """Auto set category id for product."""
        category = Category.query.filter_by(name=name).first()
        if category:
            return category.id
        raise ValueError("No such category")


class ProductInfo(db.Model):
    """ProductInfo table model."""

    __tablename__ = "product_info"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    product = db.Column(db.Integer(), db.ForeignKey("product.id"), nullable=False)
    shop = db.Column(db.Integer(), db.ForeignKey("shop.id"), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    price_rrc = db.Column(db.Integer(), nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)
    slug = db.Column(db.String(255), nullable=False)

    def __init__(self, name, product, shop, price, price_rrc, quantity, id=None):
        self.id = id
        self.name = name
        self.product = self.__set_product(product)
        self.shop = self.__set_shop(shop)
        self.price = price * 100
        self.price_rrc = price_rrc * 100
        self.quantity = quantity
        self.slug = slugify(name + " " + str(self.shop))

    def __repr__(self):
        return (
            f"{__class__.__name__}("
            f"{self.id!r}, "
            f"{self.name!r}, "
            f"{self.product!r}, "
            f"{self.shop!r}, "
            f"{self.price!r}, "
            f"{self.price_rrc!r}, "
            f"{self.quantity!r}, "
            f"{self.slug!r}"
            f")"
        )

    @staticmethod
    def __set_product(name: str) -> int:
        """Auto set product id for product."""
        product = Product.query.filter_by(name=name).first()
        if isinstance(name, int):
            return name
        if product:
            return product.id
        raise ValueError("No such product")

    @staticmethod
    def __set_shop(name) -> int:
        """Auto set shop id for product."""
        if isinstance(name, int):
            return name

        shop = Shop.query.filter_by(title=name).first()
        if shop:
            return shop.id
        raise ValueError("No such shop")


class Parameter(db.Model):
    """Parameter table model."""

    __tablename__ = "parameter"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, name, id=None):
        self.id = id
        self.name = name


class ProductParameter(db.Model):
    """Product parameter x-table model."""

    __tablename__ = "x_product_parameter"
    product_info = db.Column(
        db.Integer(), db.ForeignKey("product_info.id"), primary_key=True, nullable=False
    )
    parameter = db.Column(
        db.Integer(), db.ForeignKey("parameter.id"), primary_key=True, nullable=False
    )
    value = db.Column(db.String(255), nullable=False)

    def __init__(self, product, parameter, value):
        self.product_info = self.__set_product(product)
        self.parameter = self.__set_parameter(parameter)
        self.value = value

    # def __str__(self):
    #     return f'{self.product_info}, {self.parameter}, {self.value}'

    def __repr__(self):
        return (
            f"{__class__.__name__}("
            f"product={self.product_info!r}, "
            f"parameter={self.parameter!r}, "
            f"value={self.value!r}"
            f")"
        )

    def __hash__(self):
        return hash((self.product_info, self.parameter, self.value))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __lt__(self, other):
        return self.product_info < other.product_info

    @staticmethod
    def __set_product(name) -> int:
        """Auto set product_info id for product."""
        if isinstance(name, int):
            return name
        if not name:
            print("No name")
            input()
        pr_info = Product.query.filter_by(name=name).first()
        if not pr_info:
            print("No product")
            input()
        if pr_info:
            return pr_info.id
        raise ValueError("No such product info")

    @staticmethod
    def __set_parameter(name: str) -> int:
        """Auto set parameter id for product."""
        if isinstance(name, int):
            return name

        param = Parameter.query.filter_by(name=name).first()
        if param:
            return param.id
        raise ValueError("No such parameter")


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
