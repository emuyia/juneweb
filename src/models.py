from src import db
import secrets
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship

# association tables
post_tags = db.Table('post_tags',
                     db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                     db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                     )

album_tracks = db.Table('album_tracks',
                        db.Column('album_id', db.Integer, db.ForeignKey('album.id')),
                        db.Column('track_id', db.Integer, db.ForeignKey('track.id'))
                        )

subscription_tags = db.Table('subscription_tags',
                             db.Column('subscription_id', db.Integer, db.ForeignKey('subscription.id')),
                             db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                             )


class Post(db.Model):
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

    def __str__(self):
        return self.name


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    artist = db.Column(db.String(80), nullable=False)
    release_date = db.Column(db.String(80), nullable=False)
    cover_image = db.Column(db.String(120), nullable=True)
    tracks = relationship('Track',
                          cascade="all,delete",
                          secondary=album_tracks,
                          backref=db.backref('albums', cascade="all,delete"))
    embed = db.Column(db.Text)
    content = db.Column(db.Text)


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(50))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Subscription(db.Model):
    __tablename__ = 'subscription'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    unsubscribe_token = db.Column(db.String(32), nullable=False)
    interval = db.Column(db.String(20), nullable=False)
    last_email_sent = db.Column(db.DateTime)
    tags = db.relationship('Tag', secondary=subscription_tags,
                           backref=db.backref('subscriptions', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('email', name='uix_email'),
        db.UniqueConstraint('unsubscribe_token', name='uix_unsubscribe_token'),
    )

    # Add a constructor/initializer
    def __init__(self, email, interval):
        self.email = email
        self.interval = interval
        self.unsubscribe_token = secrets.token_hex(16)
