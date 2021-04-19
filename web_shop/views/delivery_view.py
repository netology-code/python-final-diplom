"""Delivery mock module."""
import json
import time
from celery import current_task
import requests
from flask import jsonify, make_response, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.sql.elements import and_

from web_shop import app, db, celery
from web_shop.database.models import *
from web_shop.utils.utils import create_new_item, price_to_str, sort_items
from web_shop.views.index_view import (
    add_items_to_cart,
    show_product_parameters,
)


@app.route("/delivery_responses", methods=["POST"])
def delivery_responses():
    """Delivery responses handler."""
    print(request)


@app.route("/delivery_tasks", methods=["POST"])
def delivery_tasks():
    """Delivery tasks handler."""
    order = request.get_json()
    print(111, order)
    deliver(order)
    print(222, current_task)
    return json.dumps({"report": f"Заказ №{order['order_id']} принят в доставку"})


@celery.task()
def deliver(order):
    """Delivery mock."""
    if order:
        time.sleep(10)
        headers = {"Content-Type": "application/json"}
        data = json.dumps({"report": f"Заказ №{order['order_id']} принят в доставку"})
        requests.post("http://127.0.0.1/delivery_responses", headers=headers, data=data)
        print(data)

        if order["delivery"] == "Rabbit":
            time.sleep(10)
        else:
            time.sleep(600)

        data = json.dumps({"report": f"Заказ №{order['order_id']} доставлен"})
        requests.post("http://127.0.0.1/delivery_responses", headers=headers, data=data)
        print(data)
