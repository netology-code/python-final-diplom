"""Cart view."""

from flask import make_response, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.sql.elements import and_

from web_shop import app, db
from web_shop.database.models import *
from web_shop.utils.utils import create_new_item, price_to_str, sort_items
from web_shop.views.index_view import (
    add_items_to_cart,
    show_product_parameters,
)


@app.route("/cart", methods=["GET", "POST"])
def show_cart():
    """User's cart view."""
    if request.args.get("item"):
        return show_product_parameters(request)
    order = Order.query.filter_by(
        user=current_user.id, status=OrderStateChoices.cart.name
    ).first()
    if order:
        cart_goods = OrderItem.query.filter_by(order=order.id).all()
        if cart_goods:
            items = []
            checked_items = set()
            total_sum = 0
            for good in cart_goods:
                pr_info = ProductInfo.query.filter(
                    ProductInfo.product == good.product, ProductInfo.shop == good.shop
                ).first()

                if pr_info:
                    total_sum += (
                        good.agg_price
                        if pr_info.shop_rel.shop_manager.is_active and pr_info.quantity
                        else 0
                    )
                    new_item = create_new_item(order, good, pr_info)
                    items.append(new_item)
                    if request.form.get("select_all") or request.form.get(
                        f"{pr_info.slug}_check"
                    ):
                        checked_items.add(new_item)

            items = sort_items(request, items)

            if request.method == "POST":
                if request.form.get("update"):
                    update_cart(items, request, current_user.id)
                    return make_response(redirect(request.full_path))
                if checked_items:
                    if request.form.get("submit"):
                        items_for_order = update_cart(
                            checked_items, request, current_user.id
                        )
                        add_to_order(items_for_order)
                        return make_response(redirect(url_for("list_orders")))
                    if request.form.get("delete"):
                        delete_from_cart_or_order(checked_items)
                    return make_response(redirect(request.full_path))
            return make_response(
                render_template(
                    "cart.html", items=items, total_sum=price_to_str(total_sum)
                )
            )

    return make_response(render_template("cart.html"))


def update_cart(items, request_, user_id):
    """Update cart."""
    if request.form.get("submit"):
        chosen_goods = [
            (item, int(request_.form[f"{item.slug}_cart_qty"]))
            for item in items
            if (
                request_.form.get(f"{item.slug}_cart_qty")
                and item.available
                and int(request.form[f"{item.slug}_cart_qty"])
            )
        ]
    else:
        chosen_goods = [
            (item, int(request_.form[f"{item.slug}_cart_qty"]))
            for item in items
            if request_.form.get(f"{item.slug}_cart_qty")
        ]

    chosen_goods.append(user_id)
    add_items_to_cart(chosen_goods, request_.path)
    chosen_goods.append(user_id)
    return chosen_goods


def delete_from_cart_or_order(items):
    """Delete items from cart or from order."""
    if items:
        items = list(items)

        order = Order.query.get(items[0].order)
        order.delivery_id = None
        order.delivery_sum = None
        db.session.commit()

        for item in items:
            item_to_delete = OrderItem.query.filter_by(
                order=item.order, shop=item.shop_id, product=item.product
            ).first()
            if item_to_delete:
                db.session.delete(item_to_delete)
                db.session.commit()


def add_to_order(items):
    """Add items chosen by user to his cart."""
    user = items.pop()
    if items:
        order = Order.query.filter_by(
            user=user, status=OrderStateChoices.new.name
        ).first()
        if not order:
            order = Order(user, OrderStateChoices.new.name)
            db.session.add(order)
            db.session.commit()
            db.session.flush()
            db.session.refresh(order)

        cart = items[0][0].order
        cart_goods = OrderItem.query.filter_by(order=cart).all()

        for item, quantity in items:
            ordered_item = OrderItem.query.filter(
                and_(
                    OrderItem.order == order.id,
                    OrderItem.product == item.product,
                    OrderItem.shop == item.shop_id,
                )
            ).first()
            if ordered_item:
                ordered_item.quantity += quantity
                db.session.commit()
            else:
                for good in cart_goods:
                    if good.product == item.product and good.shop == item.shop_id:
                        good.order = order.id
                        db.session.commit()

        items = [item[0] for item in items]
        delete_from_cart_or_order(items)
