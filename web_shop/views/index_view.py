"""Index view for login, logout and registration."""

from flask import flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.sql.elements import and_

from web_shop import app, db
from web_shop.database.models import *
from web_shop.utils.utils import (
    Item,
    get_product_parameters,
    opened_shops,
    price_to_str,
    sort_items,
)


@app.route("/", methods=["GET", "POST"])
def index():
    """Index view."""
    categories = sorted(Category.query.all(), key=lambda cat: cat.name)

    if request.args.get("item"):
        return show_product_parameters(request, categories)

    if categories:
        if request.args.get("cat"):
            category = Category.query.filter_by(name=request.args.get("cat")).first()
            if category:
                goods = show_goods_by_category(category, request)

                if request.method == "POST":
                    for item in goods:
                        if (
                            request.form.get(f"{item.slug}_cart_qty")
                            and int(request.form[f"{item.slug}_cart_qty"])
                            > item.stock_qty
                        ):
                            flash(
                                "Выбранное количество не может превышать количества товара на складе"
                            )
                            return make_response(redirect(request.full_path))

                    chosen_goods = [
                        (item, int(request.form[f"{item.slug}_cart_qty"]))
                        for item in goods
                        if (
                            request.form.get(f"{item.slug}_cart_qty")
                            and request.form[f"{item.slug}_cart_qty"] != "0"
                        )
                    ]
                    chosen_goods.append(current_user.id)
                    add_items_to_cart(chosen_goods, request.path)
                    return make_response(redirect(request.full_path))

                return make_response(
                    render_template(
                        "showcase.html",
                        header=category.name,
                        cats=categories,
                        items=goods,
                    )
                )
            return make_response(
                render_template("showcase.html", header=category.name, cats=categories)
            )
        return make_response(render_template("showcase.html", cats=categories))
    return make_response(render_template("showcase.html"))


def add_items_to_cart(items, request_path):
    """Add items chosen by user to his cart."""
    user = items.pop()
    if items:
        if items[0][0].order:
            order = items[0][0].order
        else:
            order = Order.query.filter_by(
                user=user, status=OrderStateChoices.cart.name
            ).first()
        if not order:
            order = Order(user)
            db.session.add(order)
            db.session.commit()
            db.session.flush()  # reset session
            db.session.refresh(order)  # get order id after insert

        order_items = []
        for item, quantity in items:
            good = OrderItem.query.filter_by(
                order=item.order if item.order else order.id,
                product=item.product,
                shop=item.shop_id,
            ).first()
            if good:
                if request_path == url_for("index"):
                    good.quantity += quantity
                elif request_path == url_for("show_cart"):
                    good.quantity = quantity
                db.session.commit()
            else:
                item = ProductInfo.query.filter_by(slug=item.slug).first()
                order_items.append(OrderItem(order.id, item.product, item.shop, quantity))
        db.session.bulk_save_objects(order_items)
        db.session.commit()


def show_goods_by_category(cat, request_):
    """Show goods by selected category on request."""
    products = Product.query.filter_by(category=cat.id).all()
    if products:
        items = set()
        for product in products:
            infos = ProductInfo.query.filter(
                and_(
                    ProductInfo.product == product.id,
                    ProductInfo.shop.in_(opened_shops()),
                    ProductInfo.quantity > 0,
                )
            ).all()
            if infos:
                pr_info: ProductInfo
                for pr_info in infos:
                    items.add(
                        Item(
                            order=None,
                            name=pr_info.name,
                            shop_id=pr_info.shop_rel.id,
                            shop_name=pr_info.shop_rel.title,
                            stock_qty=pr_info.quantity,
                            quantity=None,
                            status=None,
                            price=price_to_str(pr_info.price_rrc),
                            agg_price=None,
                            discount_price=None,
                            discount=None,
                            product=pr_info.product,
                            available=pr_info.shop_rel.shop_manager.is_active,
                            slug=pr_info.slug,
                        )
                    )
        items = sort_items(request_, items)
        return items


def show_product_parameters(request_, categories=None):
    """Show product parameters on request."""
    info: ProductInfo = ProductInfo.query.filter_by(slug=request_.args["item"]).first()
    if info:
        parameters = get_product_parameters(info.product)
        return make_response(
            render_template(
                "showcase.html", header=info.name, parameters=parameters, cats=categories,
            )
        )
    return make_response(redirect(url_for("index")))
