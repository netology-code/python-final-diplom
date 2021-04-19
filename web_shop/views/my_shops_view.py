"""Seller's shops view."""
import os
from datetime import datetime

import yaml
from flask import (
    flash,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from werkzeug.utils import secure_filename

from web_shop import app, celery, db
from web_shop.database import (
    Category,
    Parameter,
    Product,
    ProductInfo,
    ProductParameter,
    Shop,
)

BASE_URL = "/account/my_shops"


@app.route(BASE_URL, methods=["GET"])
def my_shops():
    """View for seller's shops management."""
    if not current_user.is_authenticated or current_user.user_type.name != "seller":
        return make_response(redirect(url_for("index")))
    shops = Shop.query.filter_by(user_id=current_user.id).order_by(Shop.title).all()
    return make_response(render_template("my_shops.html", shops=shops))


@app.route(BASE_URL + "/upload_file", methods=["GET", "POST"])
def upload_file():
    """Actions on file upload."""
    if not current_user.is_authenticated or current_user.user_type.name != "seller":
        return make_response(redirect(url_for("index")))
    if request.args.get("shop"):
        shop = Shop.query.filter_by(title=request.args["shop"]).first()
        if (
            shop
            and request.args["shop"] == shop.title
            and current_user.id == shop.user_id
        ):
            if request.method == "POST":
                # check if the post request has the file part
                if "file" not in request.files:
                    flash("Файл не прикреплён")
                    return make_response(redirect(request.url))
                file = request.files["file"]
                # if user does not select file, browser also
                # submit an empty part without filename
                if file.filename == "":
                    flash("Выберите файл")
                    return make_response(redirect(request.url))
                if not file or not allowed_file(file.filename):
                    flash("Допускаются только файлы формата yaml")
                    return make_response(redirect(request.url))

                secured_filename = secure_filename(file.filename)
                new_filename = save_file(file, current_user, secured_filename)
                if new_filename:
                    import_data(new_filename)
                return make_response(redirect(url_for("my_shops")))
            return make_response(render_template("upload_file.html"))
    return make_response(redirect(url_for("my_shops")))


def allowed_file(filename):
    """Check filename is correct and has valid format."""
    if isinstance(filename, str):
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
        )
    return False


@celery.task()
def import_data(filename) -> None:
    """Parse uploaded file and insert data into database."""
    with open(filename, "r", encoding="utf-8") as f:
        file = yaml.safe_load(f)
    shop = Shop.query.filter_by(title=file["shop"]).first()
    for good in file["goods"]:
        category = Category.query.filter_by(name=good["category"]).first()
        product = Product.query.filter_by(
            name=good["model"], category=category.id
        ).first()
        if not product:
            product = Product(name=good["model"], category=good["category"])
            product = add_to_database(product)

        product_info = ProductInfo.query.filter_by(
            name=good["name"], product=product.id, shop=shop.id,
        ).first()
        if not product_info:
            product_info = ProductInfo(
                name=good["name"],
                product=product.id,
                shop=shop.id,
                price=good["price"],
                price_rrc=good["price_rrc"],
                quantity=good["quantity"] if good.get("quantity") else 0,
            )
            product_info = add_to_database(product_info)
        else:
            product_info.price = int(good["price"] * 100)
            product_info.price_rrc = int(good["price_rrc"] * 100)
            product_info.quantity += good["quantity"] if good.get("quantity") else 0
            db.session.commit()

        if good.get("parameters"):
            for key in good["parameters"].keys():
                param = Parameter.query.filter_by(name=key).first()
                if not param:
                    param = Parameter(name=key)
                    param = add_to_database(param)

                product_param = ProductParameter.query.filter_by(
                    product_info=product_info.product,
                    parameter=param.id,
                    value=str(good["parameters"][key]),
                ).first()

                if not product_param:
                    product_param = ProductParameter(
                        product_info.product, param.id, str(good["parameters"][key])
                    )
                    add_to_database(product_param)


@celery.task()
def save_file(file, user, filename) -> str or None:
    """Save uploaded file.

    :param file: file-object from request
    :param user: current_user object
    :param filename: secured filename
    :return str: a new filename, including upload datetime, shop manager's email and basic filename
    """
    folder = os.path.join(app.config["UPLOAD_FOLDER"], request.args["shop"])
    os.makedirs(folder, exist_ok=True)
    filename, extension = filename.rsplit(".", 1)
    upload_time = datetime.utcnow()
    filename = ".".join(
        (
            "-".join(
                (
                    datetime.strftime(upload_time, "%Y_%m_%d__%H_%M_%S_UTC"),
                    user.email.lower(),
                    filename,
                )
            ),
            extension,
        )
    )
    path = os.path.join(folder, filename)
    file.save(path)
    with open(path, "r", encoding="utf-8") as f:
        file = yaml.safe_load(f)

    attrs = ("category", "name", "model", "price", "price_rrc")
    if not all(x in file for x in ("shop", "goods")) or not all(
        key in good for key in attrs for good in file["goods"]
    ):
        flash("Содержимое файла не соответствует требуемому формату")
        flash("Файл отклонён")
        os.remove(path)
        return

    shop = Shop.query.filter_by(title=file["shop"]).first()
    if not shop:
        flash("Файл содержит данные для незарегистрированного магазина")
        flash("Файл отклонён")
        os.remove(path)
        return

    if not shop.user_id == current_user.id:
        flash("Вы не являетесь управляющим магазина, указанного в файле")
        flash("Файл отклонён")
        os.remove(path)
        return

    shop.filename = filename
    shop.file_upload_datetime = upload_time
    db.session.commit()
    return os.path.abspath(os.path.join(folder, filename))


def add_to_database(obj):
    """Insert new object to database."""
    db.session.add(obj)
    db.session.commit()
    db.session.flush()
    db.session.refresh(obj)
    return obj
