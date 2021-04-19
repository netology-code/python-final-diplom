"""Module for confirmed orders managing by sellers."""
# import json
from typing import List

# import requests
from flask import make_response, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.sql.elements import and_

from web_shop import app, db
from web_shop.database.models import *
from web_shop.emails import create_message, send_message
from web_shop.forms import SellersOrdersForm
from web_shop.views.orders_view import get_items


@app.route("/sellers_orders", methods=["GET", "POST"])
def sellers_orders():
    """View for orders' managing by sellers."""
    if not request.args.get("status"):
        return make_response(redirect(url_for("sellers_orders") + "?status=confirmed"))

    if request.form.get("order_current_status") and request.form.get(
        "order_current_status"
    ) != request.args.get("status"):
        status = request.form["order_current_status"]
        return make_response(redirect(url_for("sellers_orders") + f"?status={status}"))

    status = request.args["status"]

    form = SellersOrdersForm()
    shops = [shop.id for shop in Shop.query.filter_by(user_id=current_user.id).all()]
    order_ids = {
        item.order for item in OrderItem.query.filter(OrderItem.shop.in_(shops)).all()
    }
    orders: List[Order] = Order.query.filter(
        and_(Order.id.in_(order_ids), Order.status == status)
    ).all()
    items = list_items(request, shops)

    if request.method == "POST":
        statuses = {
            "Заказан": ItemOrderStateChoices.ordered.name,
            "Собран": ItemOrderStateChoices.assembled.name,
            "Отменен": ItemOrderStateChoices.canceled.name,
        }
        if items:
            for item in items:
                if request.form.get(f"{item.slug}_status_select"):
                    good: OrderItem = OrderItem.query.filter_by(
                        product=item.product, shop=item.shop_id, order=item.order
                    ).first()
                    good.status = statuses[request.form[f"{item.slug}_status_select"]]
                    db.session.commit()

            goods_statuses = [
                good.status.name
                for good in OrderItem.query.filter_by(order=items[0].order).all()
            ]

            if "ordered" not in goods_statuses:
                if all(s == "assembled" for s in goods_statuses):
                    order: Order = Order.query.get(items[0].order)
                    order.status = OrderStateChoices.assembled.name
                    db.session.commit()
                    db.session.flush()
                    db.session.refresh(order)
                    message = create_message(
                        f"Изменение статуса заказа №{order.id}", order.customer.email
                    )
                    message.html = f"Ваш заказ №{order.id} {order.status.value.lower()}."
                    send_message(message)
                elif all(s == "canceled" for s in goods_statuses):
                    order: Order = Order.query.get(items[0].order)
                    order.status = OrderStateChoices.canceled.name
                    db.session.commit()
                    db.session.flush()
                    db.session.refresh(order)
                    message = create_message(
                        f"Изменение статуса заказа №{order.id}", order.customer.email
                    )
                    message.html = (
                        f"Ваш заказ №{order.id} {order.status.value.lower()}. "
                        f"Все заказанные Вами товары отсутствуют в наличии."
                    )
                    send_message(message)
                else:
                    order: Order = Order.query.get(items[0].order)
                    order.status = OrderStateChoices.assembled.name
                    db.session.commit()
                    db.session.flush()
                    db.session.refresh(order)
                    message = create_message(
                        f"Изменение статуса заказа №{order.id}", order.customer.email
                    )
                    message.html = (
                        f"Ваш заказ №{order.id} {order.status.value.lower()}.<br>"
                        f"В ходе сборки некоторые позиции были исключены из заказа.<br>"
                        f"Сумма заказа была соразмерно уменьшена.<br><br>"
                        f"Заказ передан в службу доставки {order.delivery.title}.<br><br>"
                        f"С подробностями можно ознакомиться в личном кабинете в разделе 'Заказы'."
                    )
                    send_message(message)

                if order.status.name == "assembled":
                    if order.delivery_id != 1:
                        order = Order.query.get(order.id)
                        order.status = OrderStateChoices.sent.name
                        db.session.commit()
                        message = create_message(
                            f"Изменение статуса заказа №{order.id}", order.customer.email
                        )
                        message.html = (
                            f"Ваш заказ №{order.id} {order.status.value.lower()}.<br>"
                            f"Ожидайте доставку.<br>"
                        )
                        send_message(message)
                        # data = json.dumps(
                        #     {"delivery": order.delivery.title, "order_id": order.id}
                        # )
                        # headers = {"Content-Type": "application/json"}
                        # requests.session().post(
                        #     "http://127.0.0.1/delivery_tasks", headers=headers, data=data
                        # )
                        return make_response(redirect(request.path))
                    order = Order.query.get(order.id)
                    order.status = OrderStateChoices.ready.name
                    db.session.commit()
                    message = create_message(
                        f"Изменение статуса заказа №{order.id}", order.customer.email
                    )
                    message.html = (
                        f"Ваш заказ №{order.id} {order.status.value.lower()}.<br>"
                        f"Вы можете забрать его в пункте самовывоза.<br>"
                    )
                    send_message(message)
                    return make_response(redirect(request.path))

            return make_response(redirect(request.full_path))

    return make_response(
        render_template("manage_orders.html", form=form, orders=orders, items=items)
    )


def list_items(request_, shops):
    """List all ordered items."""
    if request_.args.get("order"):
        order = request.args["order"]
        goods = OrderItem.query.filter(
            and_(OrderItem.shop.in_(shops), OrderItem.order == order)
        ).all()
        return get_items(goods, Order.query.get(order))[0]
