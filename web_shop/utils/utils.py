"""Utils module."""

from typing import NamedTuple, Union

from flask import url_for

from web_shop.database import Delivery, Parameter, ProductParameter, Shop, discount_price
from web_shop.emails import create_confirmation_token


class Item(NamedTuple):
    """A container for transferring a certain good across the code."""

    order: int or None
    name: str
    shop_id: int
    shop_name: str
    stock_qty: int
    quantity: int or None
    status: str or None
    price: int or str
    agg_price: int or str or None
    discount_price: int or str or None
    discount: int or str or None
    product: int
    available: bool
    slug: str


class GoodParameter(NamedTuple):
    """A container for transferring a certain good parameter across the code."""

    name: str
    value: Union[str, int, bool, None]


def create_new_item(order, good, pr_info):
    """Gather all the info on ordered good in one container."""
    return Item(
        order=order.id,
        name=pr_info.name,
        shop_id=pr_info.shop_rel.id,
        shop_name=pr_info.shop_rel.title,
        stock_qty=pr_info.quantity,
        quantity=good.quantity,
        status=good.status,
        price=price_to_str(pr_info.price_rrc),
        agg_price=price_to_str(good.agg_price),
        discount_price=price_to_str(discount_price(pr_info.price_rrc, good.discount)),
        discount=str(100 - int(good.discount * 100)) + "%",
        product=pr_info.product,
        available=pr_info.shop_rel.shop_manager.is_active,
        slug=pr_info.slug,
    )


def create_link(data):
    """Create confirmation link.

    :param data: any data-type to be put
    :return: an url with external access
    """
    token = create_confirmation_token(data)
    return url_for("confirm", token=token, _external=True)


def count_delivery_rate(delivery_id: int, sellers_qty: int):
    """Create confirmation link.

    :param delivery_id: id-number of chosen delivery service
    :param sellers_qty: quantity of sellers in order
    :return: delivery cost
    """
    delivery: Delivery = Delivery.query.get(delivery_id)
    k = 1
    if sellers_qty > 2:
        k = 0.85
    return delivery.rate * sellers_qty * k


def get_product_parameters(product_id):
    """Create a list of product parameters on request."""
    params = ProductParameter.query.filter_by(product_info=product_id).all()
    parameters = []
    for param in params:
        param_name = Parameter.query.get(param.parameter)
        parameters.append(GoodParameter(param_name.name, param.value))
    return parameters


def opened_shops():
    """Check shop is open and ready for orders."""
    shops = Shop.query.all()
    return [shop.id for shop in shops if shop.shop_manager.is_active]


def price_to_str(price):
    """Make db price look normal."""
    integ = list(str(price // 100))

    digits_list = []
    for _ in range(len(integ) % 3):
        digits_list.extend(integ.pop(0))

    for i in range(len(integ) // 3):
        i *= 3
        digits_list.append(" ")
        n = integ[i : i + 3]
        digits_list.extend(n)

    price_int = "".join(digits_list)

    price_rem = price % 100
    if not price_rem:
        price_rem = str(price_rem) * 2
    elif price_rem in range(1, 10):
        price_rem = "0" + str(price_rem)
    else:
        price_rem = str(price_rem)
    return ".".join((price_int, price_rem))


def sort_items(request_, items):
    """Sort goods before render."""
    if request_.args.get("sort_by") and request_.args.get("reverse"):
        return _sort_items(
            items, request_.args.get("sort_by"), request_.args.get("reverse")
        )
    if request_.args.get("sort_by"):
        return _sort_items(items, request_.args.get("sort_by"))
    return _sort_items(items)


def _sort_items(items, sort=None, reverse=False):
    """Sort goods."""
    if sort:
        if sort == "name":
            items = sorted(list(items), key=lambda i: i.name)
        elif sort == "shop":
            items = sorted(list(items), key=lambda i: i.shop_name)
        elif sort == "agg_price":
            items = sorted(list(items), key=lambda i: float("".join(i.agg_price.split())))
        elif sort == "discount":
            items = sorted(list(items), key=lambda i: int(i.discount.split("%")[0]))
        elif sort == "discount_price":
            items = sorted(
                list(items), key=lambda i: float("".join(i.discount_price.split()))
            )
        elif sort == "price":
            items = sorted(list(items), key=lambda i: float("".join(i.price.split())))
        elif sort == "stock_qty":
            items = sorted(list(items), key=lambda i: int(i.stock_qty))
        elif sort == "quantity":
            items = sorted(list(items), key=lambda i: int(i.quantity))
    else:
        items = sorted(list(items), key=lambda i: i.name)

    if reverse:
        items.reverse()

    return items
