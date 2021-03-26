"""Seller's shops view."""
import os
from datetime import datetime

from flask import (
    flash,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
    send_from_directory,
)
from flask_login import current_user
from werkzeug.utils import secure_filename

from web_shop.database import User, UserTypeChoices, Shop
from web_shop.emails import (
    create_confirmation_token,
    create_message,
    send_message,
)
from web_shop.forms import MyRegisterForm
from web_shop import app, db

BASE_URL = "/account/my_shops"


@app.route(BASE_URL, methods=["GET", "POST"])
def my_shops():
    """View for seller's shops management."""
    shops = Shop.query.filter_by(user_id=current_user.id).order_by(Shop.title).all()
    return make_response(render_template("my_shops.html", shops=shops))


@app.route(BASE_URL + "/upload_file", methods=["GET", "POST"])
def upload_file():
    """Actions on file upload."""
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

                folder = os.path.join(app.config["UPLOAD_FOLDER"], request.args["shop"])
                os.makedirs(folder, exist_ok=True)
                secured_filename = secure_filename(file.filename)
                filename, extension = secured_filename.rsplit(".", 1)
                upload_time = datetime.utcnow()
                filename = ".".join(
                    (
                        "_".join(
                            (
                                datetime.strftime(upload_time, "%Y_%m_%d__%H_%M_%S"),
                                current_user.email.lower(),
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
                return make_response(redirect(url_for("my_shops")))
            return make_response(render_template("upload_file.html"))
    return make_response(redirect(url_for("my_shops")))


def allowed_file(filename):
    """Check filename is correct and has valid format."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )
