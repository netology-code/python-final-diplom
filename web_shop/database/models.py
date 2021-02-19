"""Database table models."""
import datetime

import jwt
from flask import jsonify
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from web_shop import app, db, login_manager


class User(UserMixin, db.Model):
    """Unified user model."""

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime(), nullable=False)
    is_admin = db.Column(db.Boolean(), default=False)
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship("Role", secondary="roles_users", backref=db.backref("users", lazy="dynamic"))

    # def __init__(self, email: str, is_admin: bool, token: str, expiry: datetime):
    #     self.email = email
    #     self.is_admin = is_admin
    #     self.token = token
    #     self.expires_at = expiry

    def __repr__(self):
        return f"<User {self.username!r} {self.password!r} {self.is_admin!r} {self.expires_at!r}>"

    def set_password(self, password: str) -> None:
        """User password hash setter.

        :param password - raw password string
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """User password hash checker.

        :param password - raw password string
        :return bool
        """
        return check_password_hash(self.password_hash, password)

    def create_checking_token(self):
        """Create a token to send it via email."""
        self.expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=600)
        self.token = jwt.encode({"username": self.email, "exp": self.expires_at}, app.config["SECRET_KEY"])

    @staticmethod
    def check_token(token: str):
        """Check tokens."""
        try:
            # jwt.decode() возвращает словарь с исходными ключами
            # параметр algorithms обязательный
            jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.filter_by(token=token).first()
            if current_user:
                return True
            return False
        except Exception as e:
            return jsonify({"message": e.args[0]}), 401


class Role(db.Model):
    """Role model."""

    __tablename__ = "role"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255), nullable=True)


class RolesUsers(db.Model):
    """x-table User Roles."""

    __tablename__ = "roles_users"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column("user_id", db.Integer(), db.ForeignKey("user.id"))
    role_id = db.Column("role_id", db.Integer(), db.ForeignKey("role.id"))


@login_manager.user_loader
def load_user(id):
    """Loader for login.

    :param id - user id
    :return user string or None
    """
    return User.query.get(int(id))
