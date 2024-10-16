"""Add content_md to Post model

Revision ID: ca2955f16b75
Revises: a9ab024209b0
Create Date: 2024-10-16 00:51:16.467332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca2955f16b75'
down_revision = 'a9ab024209b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('page', schema=None) as batch_op:
        batch_op.alter_column('url',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content_md', sa.Text(), nullable=False, server_default=''))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('content_md')

    with op.batch_alter_table('page', schema=None) as batch_op:
        batch_op.alter_column('url',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)

    # ### end Alembic commands ###
