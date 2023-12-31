"""Change release_date in Album to DateTime

Revision ID: 7f8da42e22ba
Revises: f6113073d571
Create Date: 2023-09-07 18:30:53.654791

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7f8da42e22ba"
down_revision = "f6113073d571"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("album", schema=None) as batch_op:
        batch_op.alter_column(
            "release_date",
            existing_type=sa.VARCHAR(length=80),
            type_=sa.DateTime(),
            existing_nullable=False,
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("album", schema=None) as batch_op:
        batch_op.alter_column(
            "release_date",
            existing_type=sa.DateTime(),
            type_=sa.VARCHAR(length=80),
            existing_nullable=False,
        )

    # ### end Alembic commands ###
