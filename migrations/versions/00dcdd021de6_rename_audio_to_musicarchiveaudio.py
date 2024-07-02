"""rename Audio to MusicArchiveAudio

Revision ID: 00dcdd021de6
Revises: b1e8e89bf086
Create Date: 2024-03-28 21:21:49.138415

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "00dcdd021de6"
down_revision = "b1e8e89bf086"
branch_labels = None
depends_on = None


def upgrade():
    # Rename the 'audio' table to 'music_archive_audio'
    op.rename_table("audio", "music_archive_audio")


def downgrade():
    # Rename the 'music_archive_audio' table back to 'audio'
    op.rename_table("music_archive_audio", "audio")
