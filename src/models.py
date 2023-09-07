from src import db, app
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.form import InlineFormAdmin
import flask_admin
from flask import redirect, url_for, request, flash, session
from wtforms import TextAreaField
from wtforms.widgets import TextArea

# association tables
post_tags = db.Table('post_tags',
                     db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                     db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                     )

page_tags = db.Table('page_tags',
                     db.Column('page_id', db.Integer, db.ForeignKey('page.id')),
                     db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                     )

album_tracks = db.Table('album_tracks',
                        db.Column('album_id', db.Integer, db.ForeignKey('album.id')),
                        db.Column('track_id', db.Integer, db.ForeignKey('track.id'))
                        )


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    related_tags = db.relationship('Tag', secondary=page_tags, backref=db.backref('pages', lazy='dynamic'))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(DateTime)
    date_posted = db.Column(DateTime, nullable=False)
    date_updated = db.Column(DateTime)
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
    release_date = db.Column(DateTime, nullable=False)
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
    track_number = db.Column(db.Integer)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)


class AdminModelView(ModelView):
    def is_accessible(self):
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            return user.is_admin if user else False
        return False

    def inaccessible_callback(self, name, **kwargs):
        flash('You do not have access to this page.', 'error')
        return redirect(url_for('login', next=request.url))


class PageModelView(AdminModelView):
    form_columns = ('title', 'content', 'related_tags')


class TrackInlineModelView(InlineFormAdmin):
    form_columns = ('id', 'track_number', 'name', 'duration')


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get("class"):
            kwargs["class"] += " ckeditor"
        else:
            kwargs.setdefault("class", "ckeditor")
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


class PostModelView(ModelView):
    form_overrides = {
        'content': CKTextAreaField
    }


class AlbumModelView(ModelView):
    inline_models = (TrackInlineModelView(Track), )
    form_overrides = {
        'content': CKTextAreaField
    }


admin = flask_admin.Admin(app, name='junesroom', template_mode='bootstrap4', base_template='admin_base.html')

admin.add_view(PageModelView(Page, db.session))
admin.add_view(PostModelView(Post, db.session))
admin.add_view(AdminModelView(Tag, db.session))
admin.add_view(AlbumModelView(Album, db.session))
admin.add_view(AdminModelView(Track, db.session))
admin.add_view(AdminModelView(User, db.session))
