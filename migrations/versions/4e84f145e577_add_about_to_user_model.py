"""Add about to User model

Revision ID: 4e84f145e577
Revises: a0d7ace42393
Create Date: 2024-02-27 17:33:08.233595

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4e84f145e577"
down_revision = "a0d7ace42393"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("about", sa.Text(), nullable=True))
        batch_op.alter_column("role_id", existing_type=sa.INTEGER(), nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column("role_id", existing_type=sa.INTEGER(), nullable=False)
        batch_op.drop_column("about")

    # ### end Alembic commands ###