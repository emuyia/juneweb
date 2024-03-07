from src import db, app
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.form import InlineFormAdmin
import flask_admin
from flask_admin import AdminIndexView, expose
from flask import url_for, request, flash, redirect
from wtforms import TextAreaField
from wtforms.widgets import TextArea
from flask_login import UserMixin, current_user, AnonymousUserMixin

# association tables
post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id")),
)

page_tags = db.Table(
    "page_tags",
    db.Column("page_id", db.Integer, db.ForeignKey("page.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id")),
)

album_tracks = db.Table(
    "album_tracks",
    db.Column("album_id", db.Integer, db.ForeignKey("album.id")),
    db.Column("track_id", db.Integer, db.ForeignKey("track.id")),
)


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    related_tags = db.relationship(
        "Tag", secondary=page_tags, backref=db.backref("pages", lazy="dynamic")
    )
    hidden = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return "({}) {}".format(self.id, self.title[:50])


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(DateTime)
    date_posted = db.Column(DateTime, nullable=False)
    date_updated = db.Column(DateTime)
    author_id = db.Column(
        db.Integer, db.ForeignKey("user.id", name="fk_author_id"), nullable=False
    )
    author = db.relationship("User")
    tags = relationship("Tag", secondary=post_tags, backref=db.backref("posts"))
    comments = db.relationship(
        "Comment", backref="post", lazy=True, cascade="all, delete-orphan"
    )
    comments_enabled = db.Column(db.Boolean, nullable=False, default=True)

    def get_tags(self):
        return ", ".join(tag.name for tag in self.tags)

    @staticmethod
    def get_posts_by_ids(ids):
        return Post.query.filter(Post.id.in_(ids)).all()

    def __repr__(self):
        return "({}) {}".format(self.id, self.title[:50])


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "({}) {}".format(self.id, self.name[:50])


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(
        db.Integer, db.ForeignKey("post.id", name="fk_post_id"), nullable=False
    )
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(DateTime, nullable=False)
    author_id = db.Column(
        db.Integer, db.ForeignKey("user.id", name="fk_author_id"), nullable=False
    )
    author = db.relationship("User")

    def __repr__(self):
        return "({}) {}".format(self.id, self.content[:50])


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    artist = db.Column(db.String(80), nullable=False)
    release_date = db.Column(DateTime, nullable=False)
    cover_image = db.Column(db.String(120), nullable=True)
    tracks = relationship(
        "Track",
        cascade="all,delete",
        secondary=album_tracks,
        backref=db.backref("albums", cascade="all,delete"),
    )
    embed = db.Column(db.Text)
    content = db.Column(db.Text)

    def __repr__(self):
        return "({}) {} - {}".format(self.id, self.artist[:50], self.title[:50])


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(50))
    track_number = db.Column(db.Integer)

    def __repr__(self):
        return "({}) {}".format(self.id, self.name[:50])


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return "<Role {}>".format(self.name)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=True, unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(512), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    profile_picture = db.Column(db.String(500))
    about = db.Column(db.Text, nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), default=1)
    role = db.relationship("Role", backref=db.backref("users", lazy=True))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def has_role(self, role_identifier):
        return self.role is not None and self.role.name == role_identifier

    def __repr__(self):
        return "({}) {}".format(self.id, self.username)


class CustomAnonymousUser(AnonymousUserMixin):
    def has_role(self, role_identifier):
        return False


#####


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role("Admin")

    def inaccessible_callback(self, name, **kwargs):
        flash("You do not have access to this page.", "error")
        return redirect(url_for("login", next=request.url))


class MonospaceTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        kwargs["class"] = (
            kwargs.get("class", "") + " resize-by-scroll monospace"
        ).strip()
        return super(MonospaceTextAreaWidget, self).__call__(field, **kwargs)


class MonospaceTextAreaField(TextAreaField):
    widget = MonospaceTextAreaWidget()


class QuillTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        kwargs["class"] = (kwargs.get("class", "") + " quill-editor").strip()
        return super(QuillTextAreaWidget, self).__call__(field, **kwargs)


class QuillTextAreaField(TextAreaField):
    widget = QuillTextAreaWidget()


class PageModelView(AdminModelView):
    form_columns = ("title", "content", "related_tags", "hidden")
    form_overrides = {"content": MonospaceTextAreaField}

    def render_args(self):
        args = super().render_args()
        args["load_quill"] = False
        return args

    def on_model_change(self, form, model, is_created):
        model.content = form.content.data


class TrackInlineModelView(InlineFormAdmin):
    form_columns = ("id", "track_number", "name", "duration")


class QuillAdminModelView(AdminModelView):
    form_overrides = {"content": QuillTextAreaField}

    def render(self, template, **kwargs):
        kwargs["load_quill"] = True
        return super().render(template, **kwargs)

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.content = TextAreaField("Content")
        return form

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.content = TextAreaField("Content")
        return form

    def on_model_change(self, form, model, is_created):
        model.content = form["content"].data


class PostModelView(QuillAdminModelView):
    inline_models = (Comment,)


class AlbumModelView(QuillAdminModelView):
    inline_models = (TrackInlineModelView(Track),)


class AdminHomeView(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render("admin_home.html")


admin = flask_admin.Admin(
    app,
    name="junesroom",
    template_mode="bootstrap4",
    base_template="admin_base.html",
    index_view=AdminHomeView(),
)

admin.add_view(PageModelView(Page, db.session))
admin.add_view(PostModelView(Post, db.session))
admin.add_view(AdminModelView(Tag, db.session))
admin.add_view(AdminModelView(Comment, db.session))
admin.add_view(AlbumModelView(Album, db.session))
admin.add_view(AdminModelView(Track, db.session))
admin.add_view(AdminModelView(User, db.session))
