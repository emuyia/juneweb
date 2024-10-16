from src import db, app
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash
from flask_admin.contrib.sqla import ModelView
import flask_admin
from flask_admin import AdminIndexView, expose
from flask import url_for, request, flash, redirect
from wtforms import TextAreaField
from wtforms.widgets import TextArea
from flask_login import UserMixin, current_user, AnonymousUserMixin
from datetime import datetime, timezone

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


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=True)
    redirect_url = db.Column(db.String(300), nullable=True)
    content = db.Column(db.Text, nullable=False)
    related_tags = db.relationship(
        "Tag", secondary=page_tags, backref=db.backref("pages", lazy="dynamic")
    )
    hidden = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return "({}) {}".format(self.id, self.title[:50])


def current_time_utc():
    return datetime.now(timezone.utc)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content_md = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='draft')

    date_created = db.Column(DateTime(timezone=True), default=current_time_utc)
    date_posted = db.Column(DateTime(timezone=True), nullable=False, default=current_time_utc)
    date_updated = db.Column(DateTime(timezone=True), onupdate=current_time_utc)

    author_id = db.Column(
        db.Integer, db.ForeignKey("user.id", name="fk_author_id"), nullable=False
    )
    author = db.relationship("User")
    tags = relationship("Tag", secondary=post_tags, backref=db.backref("posts"))
    comments = db.relationship(
        "Comment", backref="post", lazy=True, cascade="all, delete-orphan", order_by="Comment.date_posted.asc()"
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


class PageModelView(AdminModelView):
    form_columns = ("title", "url", "redirect_url", "content", "related_tags", "hidden")
    form_overrides = {"content": MonospaceTextAreaField}

    def render(self, template, **kwargs):
        kwargs['load_ace'] = True
        return super().render(template, **kwargs)

    def on_model_change(self, form, model, is_created):
        model.content = form.content.data


class EditorMDTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        # Add classes for the widget
        kwargs.setdefault('class_', 'form-control')
        kwargs.setdefault('id', 'content_md')  # Ensure the ID matches
        return super().__call__(field, **kwargs)


class EditorMDTextAreaField(TextAreaField):
    widget = EditorMDTextAreaWidget()


class PostModelView(AdminModelView):
    inline_models = (Comment,)
    form_overrides = {'content_md': EditorMDTextAreaField}
    form_columns = ('title', 'content_md', 'status', 'tags', 'comments_enabled')

    def render(self, template, **kwargs):
        kwargs['load_editormd'] = True  # Flag to load Editor.md
        return super().render(template, **kwargs)


class DashboardView(AdminIndexView):
    def is_visible(self):
        # This view won't appear in the menu structure
        return False

    @expose("/")
    def index(self):
        # Redirect /admin/ to the desired page
        return redirect(url_for("page.index_view"))


admin = flask_admin.Admin(
    app,
    name=app.config["SITE_NAME"],
    template_mode="bootstrap4",
    base_template="admin_base.html",
    index_view=DashboardView(),
)

admin.add_view(PageModelView(Page, db.session))
admin.add_view(PostModelView(Post, db.session))
admin.add_view(AdminModelView(Tag, db.session))
admin.add_view(AdminModelView(Comment, db.session))
admin.add_view(AdminModelView(User, db.session))
