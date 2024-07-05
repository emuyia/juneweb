"""add url to Page model

Revision ID: a66d574d2e73
Revises: 92cb4fa896b9
Create Date: 2024-07-05 12:37:01.317604

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a66d574d2e73'
down_revision = '92cb4fa896b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('page', schema=None) as batch_op:
        batch_op.add_column(sa.Column('url', sa.String(length=100), nullable=True))

    # Populate the new 'url' column with the values from the 'title' column
    op.execute("UPDATE page SET url = title")

    with op.batch_alter_table('page', schema=None) as batch_op:
        batch_op.alter_column('url', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('page', schema=None) as batch_op:
        batch_op.drop_column('url')

    # ### end Alembic commands ###
