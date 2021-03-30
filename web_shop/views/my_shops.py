"""Seller's shops view."""
import os
from datetime import datetime
from pprint import pprint

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
from werkzeug.utils import secure_filename

from web_shop import app, celery, db
from web_shop.database import Shop

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
                new_filename = save_file(file, current_user, shop, secured_filename)
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
    pprint(file)
    # categories = [Category(**category) for category in file["categories"]]
    #
    # print(categories)


@celery.task()
def save_file(file, user, shop, filename) -> str:
    """Save uploaded file.

    :param file: file-object from request
    :param user: current_user object
    :param shop: database shop object
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
    file.save(os.path.join(folder, filename))
    shop.filename = filename
    shop.file_upload_datetime = upload_time
    db.session.commit()
    return os.path.abspath(os.path.join(folder, filename))
