"""Index view for login, logout and registration."""
from collections import namedtuple

from flask import make_response, redirect, render_template, request, url_for
from sqlalchemy.sql.elements import and_

from web_shop import app
from web_shop.database.models import *


@app.route("/")
def index():
    """Index view."""
    categories = Category.query.all()
    if categories:
        if request.args.get("cat") and request.args.get("item"):
            info: ProductInfo = ProductInfo.query.filter_by(
                slug=request.args["item"]
            ).first()
            if info:
                parameters = show_product_parameters(info.product)
                return make_response(
                    render_template(
                        "showcase.html",
                        header=info.name,
                        parameters=parameters,
                        cats=categories,
                    )
                )
            return make_response(redirect(url_for("index")))

        if request.args.get("cat"):
            category = Category.query.filter_by(name=request.args.get("cat")).first()
            if category:
                items = show_goods_by_category(category)
                return make_response(
                    render_template(
                        "showcase.html",
                        header=category.name,
                        cats=categories,
                        items=items,
                    )
                )
            return make_response(
                render_template("showcase.html", header=category.name, cats=categories)
            )
        return make_response(render_template("showcase.html", cats=categories))
    return make_response(render_template("base.html"))


def show_goods_by_category(cat, sort_by=None, reverse=False):
    """Show goods by selected category on request."""
    products = Product.query.filter_by(category=cat.id).all()
    if products:
        o_shops = opened_shops()
        items = set()
        for product in products:
            infos = ProductInfo.query.filter(
                and_(ProductInfo.product == product.id, ProductInfo.shop.in_(o_shops))
            ).all()
            if infos:

                for info in infos:
                    shop = Shop.query.get(info.shop)
                    item = namedtuple("item", "name, shop, price, quantity, slug")
                    price_int = str(info.price_rrc // 100)
                    price_rem = info.price_rrc % 100
                    if not price_rem:
                        price_rem = str(price_rem) * 2
                    elif price_rem in range(1, 10):
                        price_rem = "0" + str(price_rem)
                    else:
                        price_rem = str(price_rem)
                    price = ".".join((price_int, price_rem))
                    items.add(
                        item(info.name, shop.title, price, info.quantity, info.slug,)
                    )
        if not sort_by:
            items = sorted(list(items), key=lambda x: x.name)
        else:
            items = sorted(list(items), key=lambda x: x.sort_by)
        if reverse:
            items.reverse()
        return items


def show_product_parameters(product_id):
    """Show product parameters on request."""
    params = ProductParameter.query.filter_by(product_info=product_id).all()
    parameters = []
    for param in params:
        parameter = namedtuple("parameter", "name value")
        param_name = Parameter.query.get(param.parameter)
        parameters.append(parameter(param_name.name, param.value))
    return parameters


def opened_shops():
    """Check shop is open and ready for orders."""
    shops = Shop.query.all()
    return [shop.id for shop in shops if seller_is_active(shop.user_id)]


def seller_is_active(user_id):
    """Check seller is active."""
    user = User.query.get(user_id)
    if user.user_type.name == "seller":
        return user.is_active
