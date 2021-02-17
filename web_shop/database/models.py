"""Database table models."""
# from datetime import datetime

# from sqlalchemy.orm import validates
from sqlalchemy.schema import CheckConstraint

from web_shop import db


class User(db.Model):
    """Unified user model."""

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    token = db.Column(db.String(50), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (CheckConstraint("8 <= char_length(password) <= 12", name="password_length"),)

    # @validates('password')
    # def validate_password(self, password) -> str:
    #     if 8 < len(password):
    #         raise ValueError('Password is too short')
    #     elif len(password) > 12:
    #         raise ValueError('Password is too long')
    #     return password
    #
    # def __init__(self, username: str, password: str, email: str, is_admin: bool, token: str, expiry: datetime):
    #     self.username = username
    #     self.password = password if len(password) > 8 else None
    #     self.email = email
    #     self.is_admin = is_admin
    #     self.token = token
    #     self.expires_at = expiry
    #
    # def __str__(self):
    #         return f'{self.first_name} {self.last_name}'
    #
    # def __repr__(self):
    #     return f"<User {self.username!r} {self.password!r} {self.is_admin!r} {self.expires_at!r}>"


# class Advertisement(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     title = db.Column(db.String(250), nullable=False)
#     description = db.Column(db.String, nullable=True)
#     created = db.Column(db.DateTime, nullable=False)
#     modified = db.Column(db.DateTime, nullable=True)
#     owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
#     owner = db.relationship("User", backref=db.backref("advertisements"))
#
#     def __init__(self, title, desc, created, owner_id):
#         self.title = title
#         self.description = desc
#         self.created = created
#         self.owner_id = owner_id
#
#     def __repr__(self):
#         return f"<Advertisement {self.title!r} {self.description!r} {self.created!r} {self.owner_id!r} >"
