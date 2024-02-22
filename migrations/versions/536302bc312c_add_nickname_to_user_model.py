"""add nickname to User model

Revision ID: 536302bc312c
Revises: e343223b3f53
Create Date: 2024-02-22 02:40:51.166310

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "536302bc312c"
down_revision = "e343223b3f53"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("nickname", sa.String(length=50), nullable=True))

    # Fetch the username for each user and set it as their nickname
    user_table = sa.table(
        "user",
        sa.column("username", sa.String),
        sa.column("nickname", sa.String),
    )
    conn = op.get_bind()
    conn.execute(user_table.update().values(nickname=user_table.c.username))

    # After populating the nickname, alter column to not nullable
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column("nickname", nullable=False)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("nickname")

    # ### end Alembic commands ###
