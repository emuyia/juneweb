from src import app, db, mail
from src.models import Post, Tag, User, Subscription
from src.routes.auth import admin_required
from flask import render_template, request, redirect, url_for, session, flash
from sqlalchemy import func
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import DataRequired, Email
from datetime import datetime, timedelta


@app.route('/')
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
    tags = QuerySelectMultipleField('Tags', query_factory=lambda: Tag.query.all(),
                                    widget=ListWidget(html_tag='ul', prefix_label=False),
                                    option_widget=CheckboxInput())
    interval = SelectField('Summary Email Frequency', choices=[('daily', 'Daily'), ('weekly', 'Weekly'),
                                                               ('monthly', 'Monthly'), ('yearly', 'Yearly')])
    submit = SubmitField('Subscribe')


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    form = SubscriptionForm()
    if request.method == 'POST' and form.validate():
        email = form.email.data
        interval = form.interval.data
        subscription = Subscription(email=email, interval=interval)
        db.session.add(subscription)
        db.session.commit()
        return 'Subscription added!'
    return render_template('subscribe.html', form=form)


@app.route('/unsubscribe/<token>', methods=['GET'])
def unsubscribe(token):
    try:
        email = URLSafeTimedSerializer(app.config['SECRET_KEY']).loads(token, salt='unsubscribe-salt', max_age=31536000) # 1 year
        subscription = Subscription.query.filter_by(email=email).first()
        if subscription:
            db.session.delete(subscription)
            db.session.commit()
            flash('You have successfully unsubscribed.', 'success')
    except:
        flash('The unsubscribe link is invalid.', 'error')
    return redirect(url_for('subscribe'))


def send_new_post_email(post):
    subscribers = Subscription.query.all()
    with mail.connect() as conn:
        for subscriber in subscribers:
            msg = Message('New Post', recipients=[subscriber.email])
            msg.body = f'A new post has been published: {post.title}'
            conn.send(msg)


def prepare_summary_email(subscription):
    # Fetch posts that match the subscription's tags and were created after the last email was sent
    posts = Post.query.join(Post.tags).filter(
        Tag.id.in_([tag.id for tag in subscription.tags]),
        Post.date_created > subscription.last_email_sent
    ).all()

    # Prepare email body with titles and URLs of the posts
    email_body = "Here are the latest posts you've subscribed to:\n\n"
    for post in posts:
        post_url = url_for('post_detail', post_id=post.id, _external=True)  # Replace with your post detail endpoint
        email_body += f"{post.title}: {post_url}\n"

    # Prepare message
    msg = Message('Post Updates', recipients=[subscription.email])
    msg.body = email_body

    return msg


def send_summary_emails():
    subscriptions = Subscription.query.all()
    for subscription in subscriptions:
        if check_interval(subscription):
            prepare_summary_email(subscription)
            subscription.last_email_sent = datetime.now()
            db.session.commit()


def check_interval(subscription):
    intervals = {
        'daily': timedelta(days=1),
        'weekly': timedelta(weeks=1),
        'monthly': timedelta(days=30),  # Approximation
        'yearly': timedelta(days=365)   # Approximation
    }
    if subscription.last_email_sent is None or \
       datetime.now() - subscription.last_email_sent > intervals[subscription.interval]:
        return True
    return False