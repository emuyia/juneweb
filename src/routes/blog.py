from src import app, db, mail
from src.models import Post, Tag, User, Subscription
from src.routes.auth import admin_required

from flask import render_template, request, redirect, url_for, session, flash
from datetime import datetime
from sqlalchemy import func
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_mail import Message


@app.route('/blog')
def blog():
    selected_tags = request.args.get('tags')
    posts = Post.query

    if selected_tags:
        selected_tags = selected_tags.split(',')
        subquery = db.session.query(Post.id).join(Post.tags).filter(Tag.name.in_(selected_tags))\
            .group_by(Post.id).having(func.count(Tag.id) == len(selected_tags)).subquery()
        posts = posts.filter(Post.id.in_(subquery))

    posts = posts.order_by(Post.date_posted.desc()).all()
    tags = Tag.query.order_by(Tag.name).all()
    return render_template("blog.html", posts=posts, tags=tags, selected_tags=selected_tags or [])


@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get(post_id)
    return render_template("view_post.html", post=post)


@app.route("/add_post", methods=["GET", "POST"])
@app.route("/edit_post/<int:post_id>", methods=["GET", "POST"])
@admin_required
def manage_post(post_id=None):
    post = None
    if post_id:
        post = Post.query.get(post_id)
    if request.method in ["POST", "PUT"]:
        title = request.form["title"]
        content = request.form["content"]
        tag_names = request.form["tag"].split(",")  # get list of tags
        user = User.query.get(session['user_id'])
        author = user.username

        date_created_str = request.form.get("date_created")

        if date_created_str:
            date_created = datetime.strptime(date_created_str, '%Y-%m-%d')
        else:
            date_created = None

        if post:
            if title != post.title or content != post.content:
                post.date_updated = datetime.now()
            post.title = title
            post.content = content
            post.author = author
            if date_created:  # only update date_created if a new date is provided
                post.date_created = date_created
        else:
            post = Post(title=title,
                        content=content,
                        date_created=date_created,
                        date_posted=datetime.now(),
                        date_updated=datetime.now(),
                        author=author)
            db.session.add(post)
            send_new_post_email(post)

        # Clear existing tags before adding new ones
        if post:
            post.tags = []

        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name.strip()).first()
            if not tag:  # if tag doesn't exist, create it
                tag = Tag(name=tag_name.strip())
                db.session.add(tag)
            post.tags.append(tag)  # append each tag to post

        # Remove unused tags from the database
        for tag in Tag.query.all():
            if not tag.posts:
                db.session.delete(tag)

        db.session.commit()

        return redirect(url_for("blog"))
    return render_template("manage_post.html", post=post)


class SubscriptionForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Subscribe')


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    form = SubscriptionForm()
    if form.validate_on_submit():
        subscription = Subscription(email=form.email.data)
        db.session.add(subscription)
        db.session.commit()
        flash('Thanks for subscribing!', 'success')
        return redirect(url_for('subscribe'))
    return render_template('subscribe.html', title='Subscribe', form=form)


def send_new_post_email(post):
    subscribers = Subscription.query.all()
    with mail.connect() as conn:
        for subscriber in subscribers:
            msg = Message('New Post', recipients=[subscriber.email])
            msg.body = f'A new post has been published: {post.title}'
            conn.send(msg)

