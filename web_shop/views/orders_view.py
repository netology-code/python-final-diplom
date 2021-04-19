"""Orders view module."""
from datetime import datetime
from typing import List

from flask import flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.sql.elements import and_

from web_shop import app, celery, db
from web_shop.database.models import *
from web_shop.emails import create_message, send_message
from web_shop.utils.utils import create_link, create_new_item, price_to_str, sort_items
from web_shop.views.cart_view import delete_from_cart_or_order
from web_shop.views.index_view import show_product_parameters


@app.route("/orders", methods=["GET", "POST"])
def list_orders():
    """Orders view."""
    if not request.args.get("type"):
        return make_response(redirect(url_for("list_orders") + "?type=new"))

    if request.args.get("item"):
        return show_product_parameters(request)

    statuses = dict(
        new=dict(
            status=OrderStateChoices.new.name, header="новые", template="new_order.html"
        ),
        awaiting=dict(
            status=OrderStateChoices.awaiting.name,
            header="неподтвержденные",
            template="orders.html",
        ),
        confirmed=dict(
            status=OrderStateChoices.confirmed.name,
            header="подтвержденные",
            template="orders.html",
        ),
        assembled=dict(
            status=OrderStateChoices.assembled.name,
            header="собранные",
            template="orders.html",
        ),
        sent=dict(
            status=OrderStateChoices.sent.name,
            header="отправленные",
            template="orders.html",
        ),
        delivered=dict(
            status=OrderStateChoices.delivered.name,
            header="доставленные",
            template="orders.html",
        ),
        canceled=dict(
            status=OrderStateChoices.canceled.name,
            header="отмененные",
            template="orders.html",
        ),
        ready=dict(
            status=OrderStateChoices.ready.name,
            header="готовые к выдаче",
            template="orders.html",
        ),
    )

    if request.args.get("type") and request.args.get("type") in statuses:
        status = request.args["type"]
    else:
        status = "new"

    orders_list: List[Order] = (
        Order.query.filter_by(
            user=current_user.id, status=statuses[status]["status"]
        ).all()
        if status
        in (
            "awaiting",
            "confirmed",
            "sent",
            "assembled",
            "delivered",
            "canceled",
            "ready",
        )
        else None
    )
    if orders_list:
        orders_list = sorted(orders_list, key=lambda _order: _order._last_change)
        orders_list.reverse()

    if request.args.get("order") and request.args["order"].isdigit():
        order = Order.query.get(request.args["order"])
        if not order:
            flash("У вас нет такого заказа")
            return make_response(redirect(request.full_path.split("&", 1)[0]))

        if order.user != current_user.id:
            flash("У вас нет такого заказа")
            return make_response(redirect(request.full_path.split("&", 1)[0]))

        if status != order.status.name:
            if order.status.name in (
                "awaiting",
                "confirmed",
                "assembled",
                "sent",
                "delivered",
                "canceled",
                "ready",
            ):
                flash("Данный заказ не относится к этой категории.")
                flash(f'Перейдите в категорию "{order.status.value}ные"')
                return make_response(redirect(request.full_path.split("&", 1)[0]))

            flash("У вас нет такого заказа")
            return make_response(redirect(request.full_path.split("&", 1)[0]))

    else:
        order = (
            Order.query.filter_by(user=current_user.id, status=statuses[status]["status"])
            .order_by(Order._last_change.desc())
            .first()
        )

    if order:
        cart_goods = OrderItem.query.filter_by(order=order.id).all()
        if cart_goods:
            items, checked_items, total_sum = get_items(cart_goods, order)
            items = sort_items(request, items)

            if request.method == "POST":
                if request.form.get("cancel"):
                    return cancel_order(order)
                if checked_items:
                    if request.form.get("delete"):
                        delete_from_cart_or_order(checked_items)
                    return make_response(redirect(url_for("list_orders")))

                if not order.delivery_id and not request.form.get("delivery"):
                    flash("Укажите способ доставки")
                    return make_response(redirect(url_for("list_orders")))
                if request.form.get("update"):
                    set_delivery(request, order)
                    update_order(items, request)
                    return make_response(redirect(request.full_path))
                if request.form.get("submit"):
                    set_delivery(request, order)
                    order = create_order(items, request)
                    flash(f"Заказ №{order.id} успешно оформлен!")
                    flash("Проверьте вашу почту и подтвердите заказ в течение 10 минут.")
                    return make_response(
                        redirect(url_for("list_orders") + "?type=awaiting")
                    )
                flash("Невозможно сформировать заказ.")
                flash("Отсутствуют доступные товары.")
                return make_response(redirect(url_for("list_orders")))

            return make_response(
                render_template(
                    statuses[status]["template"],
                    header=statuses[status]["header"],
                    orders_list=orders_list,
                    items=items,
                    delivery_name=order.delivery.title if order.delivery_id else None,
                    delivery_sum=price_to_str(order.delivery_sum)
                    if order.delivery_sum
                    else order.delivery_sum,
                    total_sum=price_to_str(
                        total_sum + order.delivery_sum
                        if order.delivery_sum
                        else total_sum
                    ),
                )
            )

    return make_response(
        render_template(
            statuses[status]["template"],
            header=statuses[status]["header"],
            orders_list=orders_list,
        )
    )


@celery.task()
def update_order(items, request_):
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

    for item, quantity in chosen_goods:
        ordered_item = OrderItem.query.filter(
            and_(
                OrderItem.order == item.order,
                OrderItem.product == item.product,
                OrderItem.shop == item.shop_id,
            )
        ).first()
        if ordered_item:
            ordered_item.quantity = quantity
            db.session.commit()

    return chosen_goods


@celery.task()
def create_order(items, request_):
    """Create an order from cart."""
    update_order(items, request_)
    if items:
        order = Order.query.filter_by(
            user=current_user.id, status=OrderStateChoices.awaiting.name
        ).first()

        if not order:
            order = Order(user=current_user.id, status=OrderStateChoices.awaiting.name,)

        cart: Order = Order.query.get(items[0].order)
        order.delivery_id = cart.delivery_id
        order.delivery_sum = cart.delivery_sum

        cart.delivery_sum, cart.delivery_id = None, None

        db.session.add(order)
        db.session.commit()
        db.session.flush()
        db.session.refresh(order)

        for item in items:
            good = OrderItem.query.filter_by(
                order=item.order, shop=item.shop_id, product=item.product
            ).first()
            if good:
                good.order = order.id
                db.session.commit()

        link = create_link((current_user.email, order.id, 600))
        message = create_message("Подтверждение заказа", current_user.email)
        message.html = (
            f"Для подтверждения вашего заказа на WebShop перейдите по ссылке: {link}"
        )
        send_message(message)
        return order


@celery.task()
def confirm_order(order):
    """Confirm order."""
    goods: List[OrderItem] = OrderItem.query.filter_by(order=order.id).all()
    items, _, total_sum = get_items(goods, order)
    for item in items:
        good: ProductInfo = ProductInfo.query.filter_by(
            product=item.product, shop=item.shop_id
        ).first()
        if not (good.quantity >= item.quantity and good.shop_rel.shop_manager.is_active):
            cart: Order = Order.query.filter_by(
                user=current_user.id, status=OrderStateChoices.cart.name
            ).first()
            for good_ in goods:
                good_.order = cart.id
                good_.quantity = 0
                db.session.commit()

            db.session.delete(order)
            db.session.commit()

            message = create_message("Отмена заказа", current_user.email)
            message.html = (
                "Ваш последний заказ был отменён вследствие отсутствия некоторых из указанных вами товаров.<br>"
                "Все указанные вами позиции были перемещены в вашу корзину.<br>"
                "Пожалуйста, выберите подходящие для вас товары из имеющихся в наличии и сформируйте новый заказ."
            )
            send_message(message)

            flash(
                f"Во время ожидания подтверждения заказа №{order.id} у поставщиков произошли изменения."
            )
            flash("Заказ удалён, все товары из заказа перемещены в Корзину.")
            flash("Оформите новый заказ.")
            return make_response(redirect(url_for("show_cart")))

    flash(f"Заказ №{order.id} успешно подтверждён.")
    return items, total_sum


@celery.task()
def get_items(cart_goods, order):
    """Get ordered items."""
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
                if (
                    pr_info.shop_rel.shop_manager.is_active
                    and pr_info.quantity
                    and good.status.name != "canceled"
                )
                or (
                    good.order_rel.status.name
                    in (
                        "awaiting",
                        "confirmed",
                        "sent",
                        "assembled",
                        "delivered",
                        "canceled",
                        "ready",
                    )
                    and good.status.name != "canceled"
                )
                else 0
            )
            new_item = create_new_item(order, good, pr_info)
            items.append(new_item)

            if request.form.get("select_all") or request.form.get(
                f"{pr_info.slug}_check"
            ):
                checked_items.add(new_item)

    return items, checked_items, total_sum


@celery.task()
def cancel_order(order):
    """Cancel order."""
    order.status = OrderStateChoices.canceled.name
    db.session.commit()

    message = create_message(f"Отмена заказа №{order.id}", current_user.email)
    message.html = f"Вы самостоятельно отменили свой заказ №{order.id}.<br>"
    send_message(message)

    return make_response(redirect(url_for("list_orders") + "?type=canceled"))


@celery.task()
def send_messages_on_order_confirmation(order, items, total_sum):
    """Send emails to customer and sellers after the order was confirmed by customer."""
    shop_emails = dict()
    customer_order = list()

    for item in items:
        good: ProductInfo = ProductInfo.query.filter_by(
            product=item.product, shop=item.shop_id
        ).first()
        good.quantity -= item.quantity
        db.session.commit()

        email = good.shop_rel.shop_manager.email

        if email not in shop_emails:
            shop_emails[email] = []

        ordered_goods = dict(
            seller=item.shop_name,
            prod=good.name,
            price=item.price,
            qty=item.quantity,
            disc=item.discount,
            disc_price=item.discount_price,
            overall=item.agg_price,
        )
        shop_emails[email].append(ordered_goods)
        customer_order.append(ordered_goods)

    order.status = OrderStateChoices.confirmed.name
    order._last_change = datetime.utcnow()
    db.session.commit()

    customer_address: Contact = Contact.query.filter_by(user=current_user.id).first()

    for email in shop_emails:
        message = create_message(f"Заказ №{order.id}", email)
        message.html = (
            "<b>Заказанные позиции:</b><br>"
            "<table border='1'>"
            "<tr>"
            "<th>Продавец</th>"
            "<th>Товар</th>"
            "<th>Цена за 1 ед.</th>"
            "<th>Кол-во</th>"
            "<th>Скидка</th>"
            "<th>Цена со скидкой</th>"
            "<th>Cтоимость</th>"
            "</tr>"
        )
        for item in shop_emails[email]:
            message.html += (
                f"<tr>"
                f"<td>{item['seller']}</td>"
                f"<td>{item['prod']}</td>"
                f"<td>{item['price']}</td>"
                f"<td>{item['qty']}</td>"
                f"<td>{item['disc']}</td>"
                f"<td>{item['disc_price']}</td>"
                f"<td>{item['overall']}</td>"
                f"</tr>"
            )
        message.html += "</table><br>"
        message.html += (
            f"<b>Покупатель:</b> "
            f"{order.customer.last_name} {order.customer.first_name}<br>"
        )

        if customer_address:
            message.html += (
                f"<br><b>Адрес доставки:</b>"
                f"<b>Индекс</b>: {customer_address.zip_code} <br>"
                f"<b>Город</b>: {customer_address.city} <br>"
                f"<b>Улица</b>: {customer_address.street} <br>"
                f"<b>Дом</b>: {customer_address.house} <br>"
                f"<b>Корпус</b>: {customer_address.structure} <br>"
                f"<b>Строение</b>: {customer_address.building} <br>"
                f"<b>Квартира</b>: {customer_address.apartment} <br>"
                f"<b>Телефон</b>: {customer_address.phone} <br>"
                f"<br>"
            )
        else:
            message.html += f"<br><b>Адрес доставки:</b> {customer_address}"
        send_message(message)

    message = create_message(f"Заказ №{order.id}", current_user.email)
    message.html = (
        "<b>Заказанные позиции:</b><br>"
        "<table border='1'>"
        "<tr>"
        "<th>Продавец</th>"
        "<th>Товар</th>"
        "<th>Цена за 1 ед.</th>"
        "<th>Кол-во</th>"
        "<th>Скидка</th>"
        "<th>Цена со скидкой</th>"
        "<th>Cтоимость</th>"
        "</tr>"
    )
    for item in customer_order:
        message.html += (
            f"<tr>"
            f"<td>{item['seller']}</td>"
            f"<td>{item['prod']}</td>"
            f"<td>{item['price']}</td>"
            f"<td>{item['qty']}</td>"
            f"<td>{item['disc']}</td>"
            f"<td>{item['disc_price']}</td>"
            f"<td>{item['overall']}</td>"
            f"</tr>"
        )
    message.html += "</table><br>"
    message.html += (
        f"<br><b>Общая стоимость заказа:</b> {price_to_str(total_sum)} руб.<br>"
    )
    if customer_address:
        message.html += (
            f"<br><b>Адрес доставки:</b>"
            f"<b>Индекс</b>: {customer_address.zip_code} <br>"
            f"<b>Город</b>: {customer_address.city} <br>"
            f"<b>Улица</b>: {customer_address.street} <br>"
            f"<b>Дом</b>: {customer_address.house} <br>"
            f"<b>Корпус</b>: {customer_address.structure} <br>"
            f"<b>Строение</b>: {customer_address.building} <br>"
            f"<b>Квартира</b>: {customer_address.apartment} <br>"
            f"<b>Телефон</b>: {customer_address.phone} <br>"
            f"<br>"
        )
    else:
        message.html += f"<br><b>Адрес доставки:</b> {customer_address}"

    send_message(message)


def set_delivery(request_, order):
    """Set delivery id to order."""
    if request_.form.get("delivery"):
        delivery = Delivery.query.filter_by(title=request_.form["delivery"]).first()
        order.delivery_id = delivery.id
        order.delivery_sum = order._delivery_sum()
        db.session.commit()
