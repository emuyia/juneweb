"""Backfill content_md for existing posts

Revision ID: 6cc62e5f0d4e
Revises: ca2955f16b75
Create Date: 2024-10-16 02:42:03.285216

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
import html2text


# revision identifiers, used by Alembic.
revision = '6cc62e5f0d4e'
down_revision = 'ca2955f16b75'
branch_labels = None
depends_on = None

Base = declarative_base()

class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    content_md = Column(Text)

def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    posts = session.query(Post).all()

    for post in posts:
        if post.content_md in (None, ''):
            markdown_content = html2text.html2text(post.content)
            post.content_md = markdown_content

    session.commit()

    session.close()
    # ### end Alembic commands ###


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    posts = session.query(Post).all()

    for post in posts:
        post.content_md = None

    session.commit()

    session.close()
    # ### end Alembic commands ###
