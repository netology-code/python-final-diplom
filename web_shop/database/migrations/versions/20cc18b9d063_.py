"""empty message

Revision ID: 20cc18b9d063
Revises:
Create Date: 2021-04-19 11:35:52.367123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20cc18b9d063"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("Название", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "parameter",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("last_name", sa.String(length=255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "user_type",
            sa.Enum("seller", "customer", "delivery", name="usertypechoices"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "contact",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user", sa.Integer(), nullable=False),
        sa.Column("zip_code", sa.String(length=6), nullable=True),
        sa.Column("city", sa.String(length=50), nullable=True),
        sa.Column("street", sa.String(length=100), nullable=True),
        sa.Column("house", sa.String(length=15), nullable=True),
        sa.Column("structure", sa.String(length=15), nullable=True),
        sa.Column("building", sa.String(length=15), nullable=True),
        sa.Column("apartment", sa.String(length=15), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(
            ["user"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "delivery",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("rate", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("title"),
        sa.UniqueConstraint("url"),
    )
    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category"],
            ["category.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "shop",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=True),
        sa.Column("filename", sa.String(length=255), nullable=True),
        sa.Column("file_upload_datetime", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("filename"),
        sa.UniqueConstraint("title"),
        sa.UniqueConstraint("url"),
    )
    op.create_table(
        "order",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user", sa.Integer(), nullable=False),
        sa.Column("_created", sa.DateTime(), nullable=False),
        sa.Column("_last_change", sa.DateTime(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "cart",
                "new",
                "awaiting",
                "confirmed",
                "assembled",
                "sent",
                "delivered",
                "canceled",
                "ready",
                name="orderstatechoices",
            ),
            nullable=False,
        ),
        sa.Column("delivery_id", sa.Integer(), nullable=True),
        sa.Column("delivery_sum", sa.Integer(), nullable=True),
        sa.Column("contact", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["contact"],
            ["contact.id"],
        ),
        sa.ForeignKeyConstraint(
            ["delivery_id"],
            ["delivery.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "product_info",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("product", sa.Integer(), nullable=False),
        sa.Column("shop", sa.Integer(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("price_rrc", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["product"],
            ["product.id"],
        ),
        sa.ForeignKeyConstraint(
            ["shop"],
            ["shop.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "x_order_item",
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("product", sa.Integer(), nullable=False),
        sa.Column("shop", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ordered", "assembled", "canceled", name="itemorderstatechoices"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["order"],
            ["order.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product"],
            ["product.id"],
        ),
        sa.ForeignKeyConstraint(
            ["shop"],
            ["shop.id"],
        ),
        sa.PrimaryKeyConstraint("order", "product", "shop"),
    )
    op.create_table(
        "x_product_parameter",
        sa.Column("product_info", sa.Integer(), nullable=False),
        sa.Column("parameter", sa.Integer(), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["parameter"],
            ["parameter.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_info"],
            ["product_info.id"],
        ),
        sa.PrimaryKeyConstraint("product_info", "parameter"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("x_product_parameter")
    op.drop_table("x_order_item")
    op.drop_table("product_info")
    op.drop_table("order")
    op.drop_table("shop")
    op.drop_table("product")
    op.drop_table("delivery")
    op.drop_table("contact")
    op.drop_table("user")
    op.drop_table("parameter")
    op.drop_table("category")
    # ### end Alembic commands ###
