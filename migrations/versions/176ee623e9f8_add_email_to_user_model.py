"""Add email to User model

Revision ID: 176ee623e9f8
Revises: 54c54a006adb
Create Date: 2024-02-21 17:34:01.538216

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "176ee623e9f8"
down_revision = "54c54a006adb"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("email", sa.String(length=50), nullable=True))
        batch_op.create_unique_constraint(
            "unique_email", ["email"]
        )  # Name the constraint

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_constraint(
            "unique_email", type_="unique"
        )  # Use the named constraint
        batch_op.drop_column("email")

    # ### end Alembic commands ###
