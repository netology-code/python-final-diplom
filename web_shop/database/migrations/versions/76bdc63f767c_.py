"""empty message

Revision ID: 76bdc63f767c
Revises: 6f646c5149ac
Create Date: 2021-02-23 16:43:29.019461

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "76bdc63f767c"
down_revision = "6f646c5149ac"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("user", sa.Column("is_active", sa.Boolean(), nullable=True))
    op.drop_column("user", "active")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user", sa.Column("active", sa.BOOLEAN(), server_default=sa.text("false"), autoincrement=False, nullable=True)
    )
    op.drop_column("user", "is_active")
    # ### end Alembic commands ###
