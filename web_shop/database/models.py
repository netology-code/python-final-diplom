"""Database table models."""
import enum
from datetime import datetime

from flask_login import UserMixin
from slugify import slugify
from sqlalchemy import distinct, func
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from web_shop import db, login_manager

__all__ = [
    "Category",
    "Contact",
    "Delivery",
    "ItemOrderStateChoices",
    "Order",
    "OrderItem",
    "OrderStateChoices",
    "Shop",
    "Product",
    "ProductParameter",
    "Parameter",
    "ProductInfo",
    "User",
    "UserTypeChoices",
    "discount_price",
    "load_user",
]


class ItemOrderStateChoices(enum.Enum):
    """Order state choices."""

    ordered = "Заказан"
    assembled = "Собран"
    canceled = "Отменен"


class OrderStateChoices(enum.Enum):
    """Order state choices."""

    cart = "Статус корзины"
    new = "Новый"
    awaiting = "Ожидает подтверждения"
    confirmed = "Подтвержден"
    assembled = "Собран"
    sent = "Отправлен"
    delivered = "Доставлен"
    canceled = "Отменен"
    ready = "Готов к выдаче"


class UserTypeChoices(enum.Enum):
    """User types choices."""

    seller = "Продавец"
    customer = "Покупатель"
    delivery = "Доставка"


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
    confirmed_at = db.Column(db.DateTime(), nullable=True)
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
        self.file_upload_datetime = (
            file_upload_datetime if file_upload_datetime else datetime.utcnow()
        )
        self.user_id = user_id

    def __repr__(self):
        return self.title


class Delivery(db.Model):
    """Shop delivery service model."""

    __tablename__ = "delivery"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    rate = db.Column(db.Integer(), nullable=False)
    url = db.Column(db.String(255), nullable=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    manager = relationship("User")

    def __init__(self, title, user_id, rate, id=None, url=None):
        self.id = id
        self.title = title
        self.url = url
        self.user_id = user_id
        self.rate = rate

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
    cat_rel = relationship("Category")

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
    product_rel = relationship("Product")
    shop_rel = relationship("Shop")

    def __init__(self, name, product, shop, price, price_rrc, quantity, id=None):
        self.id = id
        self.name = name
        self.product = self.__set_product(product)
        self.shop = self.__set_shop(shop)
        self.price = int(price * 100)
        self.price_rrc = int(price_rrc * 100)
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
        if isinstance(name, int):
            return name
        product = Product.query.filter_by(name=name).first()
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
        db.Integer(), db.ForeignKey("product_info.id"), primary_key=True, nullable=False,
    )
    parameter = db.Column(
        db.Integer(), db.ForeignKey("parameter.id"), primary_key=True, nullable=False,
    )
    value = db.Column(db.String(255), nullable=False)
    p_info = relationship("ProductInfo")
    param_rel = relationship("Parameter")

    def __init__(self, product, parameter, value):
        self.product_info = self.__set_product(product)
        self.parameter = self.__set_parameter(parameter)
        self.value = value

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


class Order(db.Model):
    """Order model."""

    __tablename__ = "order"
    id = db.Column(db.Integer(), primary_key=True)
    user = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
    _created = db.Column(db.DateTime(), nullable=False)
    _last_change = db.Column(db.DateTime(), nullable=False)
    status = db.Column(
        db.Enum(OrderStateChoices), default=OrderStateChoices.cart, nullable=False
    )
    delivery_id = db.Column(db.Integer(), db.ForeignKey("delivery.id"), nullable=True)
    delivery_sum = db.Column(db.Integer())
    contact = db.Column(db.Integer(), db.ForeignKey("contact.id"), nullable=True)
    customer = relationship("User")
    delivery = relationship("Delivery")

    def __init__(self, user, status=None, dt=None, contact=None, delivery=None, id=None):
        self.id = id
        self.user = user
        self._created = datetime.utcnow()
        self._last_change = dt if dt else datetime.utcnow()
        self.status = status
        self.contact = contact
        self.delivery_id = delivery
        self.delivery_sum = self._delivery_sum()

    dt = property()

    @dt.getter
    def created(self):
        return self._created.strftime("%d.%m.%Y %H:%M:%S")

    @dt.getter
    def last_change(self):
        return self._last_change.strftime("%d.%m.%Y %H:%M:%S")

    def _delivery_sum(self):
        if self.delivery_id:
            sellers = (
                db.session.query(
                    func.count(distinct(OrderItem.shop)), OrderItem.order == self.id
                )
                .group_by(OrderItem.order)
                .first()[0]
            )
            delivery: Delivery = Delivery.query.get(self.delivery_id)
            k = 1
            if sellers > 2:
                k = 0.85
            return delivery.rate * sellers * k


class OrderItem(db.Model):
    """Model for goods in order."""

    __tablename__ = "x_order_item"
    order = db.Column(
        db.Integer(), db.ForeignKey("order.id"), primary_key=True, nullable=False,
    )
    product = db.Column(
        db.Integer(), db.ForeignKey("product.id"), primary_key=True, nullable=False,
    )
    shop = db.Column(
        db.Integer(), db.ForeignKey("shop.id"), primary_key=True, nullable=False
    )
    status = db.Column(
        db.Enum(ItemOrderStateChoices),
        default=ItemOrderStateChoices.ordered,
        nullable=False,
    )
    quantity = db.Column(db.Integer(), nullable=False)
    order_rel = relationship("Order")
    shop_rel = relationship("Shop")
    product_rel = relationship("Product")

    def __init__(self, order, product, shop, quantity, status=None):
        self.order = order
        self.product = product
        self.shop = self.__set_shop(shop)
        self.quantity = quantity
        self.status = status if status else ItemOrderStateChoices.ordered

    @property
    def discount(self):
        if self.quantity < 4:
            return 1
        if 4 <= self.quantity < 7:
            return 0.95
        if 7 <= self.quantity < 10:
            return 0.90
        if self.quantity >= 10:
            return 0.85

    @staticmethod
    def __set_shop(shop_name):
        if isinstance(shop_name, int):
            return shop_name
        shop = Shop.query.filter_by(title=shop_name).first()
        return shop.id

    @property
    def agg_price(self):
        pr_info = ProductInfo.query.filter_by(
            product=self.product, shop=self.shop
        ).first()
        price = discount_price(pr_info.price_rrc, self.discount) * self.quantity
        if price < pr_info.price * self.quantity:
            return pr_info.price * self.quantity
        return price


class Contact(db.Model):
    """User shipping address model."""

    __tablename__ = "contact"
    id = db.Column(db.Integer(), primary_key=True)
    user = db.Column(db.ForeignKey("user.id"), nullable=False)
    zip_code = db.Column(db.String(6))
    city = db.Column(db.String(50))
    street = db.Column(db.String(100))
    house = db.Column(db.String(15), nullable=True)
    structure = db.Column(db.String(15), nullable=True)
    building = db.Column(db.String(15), nullable=True)
    apartment = db.Column(db.String(15), nullable=True)
    phone = db.Column(db.String(20))
    addressee = relationship("User")

    def __init__(
        self,
        user,
        phone,
        zip_code,
        city,
        street,
        house=None,
        structure=None,
        building=None,
        apartment=None,
        id=None,
    ):
        self.id = id
        self.user = user
        self.phone = phone
        self.zip_code = zip_code
        self.city = city
        self.street = street
        self.house = house
        self.structure = structure
        self.building = building
        self.apartment = apartment


@login_manager.user_loader
def load_user(id):
    """Load user from database for login.

    :param id - user id
    :return user string or None
    """
    return User.query.get(int(id))


def discount_price(price, discount):
    """Calculate price with discount."""
    return int(round(price * discount))
