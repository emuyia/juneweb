import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database.db')
db_uri = 'sqlite:///' + db_path

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

db = SQLAlchemy(app)

post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('blog_post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

album_tracks = db.Table('album_tracks',
    db.Column('album_id', db.Integer, db.ForeignKey('album.id')),
    db.Column('track_id', db.Integer, db.ForeignKey('track.id'))
)


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(DateTime)
    date_posted = db.Column(DateTime, nullable=False)
    date_updated = db.Column(DateTime, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    tags = relationship('Tag', secondary=post_tags, backref=db.backref('posts'))
    def get_tags(self):
        return ', '.join(tag.name for tag in self.tags)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    artist = db.Column(db.String(80), nullable=False)
    release_date = db.Column(db.String(80), nullable=False)
    cover_image = db.Column(db.String(120), nullable=True)
    tracks = relationship('Track', secondary=album_tracks, backref=db.backref('albums'))


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(50))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


with app.app_context():
    db.drop_all()
    db.create_all()

    new_album = Album(title="Mahjong Hospital", artist="Daffodil", release_date="20230710",
                      cover_image="https://images2.imgbox.com/34/2a/c6hF2yJh_o.jpg")

    track1 = Track(name="Track 1", duration="3:45")
    track2 = Track(name="Track 2", duration="4:30")
    # add more tracks as needed

    new_album.tracks.append(track1)
    new_album.tracks.append(track2)
    # append more tracks as needed

    db.session.add(new_album)
    db.session.commit()

