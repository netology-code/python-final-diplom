"""Index view for login, logout and registration."""
from collections import namedtuple

from flask import make_response, render_template, request

from web_shop import app
from web_shop.database.models import *


@app.route("/")
def index():
    """Index view."""
    categories = Category.query.all()
    if request.args.get("cat"):
        category = Category.query.filter_by(name=request.args.get("cat")).first()
        if category:
            products = Product.query.filter_by(category=category.id).all()
            if products:
                items = set()
                for product in products:
                    infos = ProductInfo.query.filter_by(product=product.id).all()
                    if infos:
                        for info in infos:
                            shop = Shop.query.get(info.shop)
                            item = namedtuple("item", "name, shop, price, quantity")
                            items.add(
                                item(info.name, shop.title, info.price_rrc, info.quantity)
                            )
                items = sorted(list(items), key=lambda x: x.name)
                return make_response(
                    render_template(
                        "base.html", header=category.name, cats=categories, items=items
                    )
                )
        return make_response(
            render_template("base.html", header=category.name, cats=categories)
        )
    return make_response(render_template("base.html", cats=categories))
