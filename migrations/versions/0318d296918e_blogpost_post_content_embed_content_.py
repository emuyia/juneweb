"""BlogPost>Post, content>embed, content_main>content

Revision ID: 0318d296918e
Revises: bd804d02f78d
Create Date: 2023-07-09 07:00:27.129785

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0318d296918e'
down_revision = 'bd804d02f78d'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('blog_post', 'post')
    op.alter_column('album', 'content', new_column_name='embed')
    op.alter_column('album', 'content_main', new_column_name='content')


def downgrade():
    op.rename_table('post', 'blog_post')
    op.alter_column('album', 'embed', new_column_name='content')
    op.alter_column('album', 'content', new_column_name='content_main')
