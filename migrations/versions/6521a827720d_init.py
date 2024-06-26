"""init

Revision ID: 6521a827720d
Revises: 
Create Date: 2024-01-10 21:01:08.087740

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6521a827720d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "album",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=80), nullable=False),
        sa.Column("artist", sa.String(length=80), nullable=False),
        sa.Column("release_date", sa.DateTime(), nullable=False),
        sa.Column("cover_image", sa.String(length=120), nullable=True),
        sa.Column("embed", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "page",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tag",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "track",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("duration", sa.String(length=50), nullable=True),
        sa.Column("track_number", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password", sa.String(length=512), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=True),
        sa.Column("profile_picture", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "album_tracks",
        sa.Column("album_id", sa.Integer(), nullable=True),
        sa.Column("track_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["album_id"],
            ["album.id"],
        ),
        sa.ForeignKeyConstraint(
            ["track_id"],
            ["track.id"],
        ),
    )
    op.create_table(
        "page_tags",
        sa.Column("page_id", sa.Integer(), nullable=True),
        sa.Column("tag_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["page_id"],
            ["page.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tag.id"],
        ),
    )
    op.create_table(
        "post",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column("date_posted", sa.DateTime(), nullable=False),
        sa.Column("date_updated", sa.DateTime(), nullable=True),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("comments_enabled", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"], name="fk_author_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "comment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("date_posted", sa.DateTime(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"], name="fk_author_id"),
        sa.ForeignKeyConstraint(["post_id"], ["post.id"], name="fk_post_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "post_tags",
        sa.Column("post_id", sa.Integer(), nullable=True),
        sa.Column("tag_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["post_id"],
            ["post.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tag.id"],
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("post_tags")
    op.drop_table("comment")
    op.drop_table("post")
    op.drop_table("page_tags")
    op.drop_table("album_tracks")
    op.drop_table("user")
    op.drop_table("track")
    op.drop_table("tag")
    op.drop_table("page")
    op.drop_table("album")
    # ### end Alembic commands ###
