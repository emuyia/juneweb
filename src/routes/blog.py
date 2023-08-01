from src import app, db
from src.models import Post, Tag, User
from src.forms import PostForm
from src.routes.auth import admin_required
from flask import render_template, request, redirect, url_for, session
from sqlalchemy import func
from datetime import datetime


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

    form = PostForm()

    if form.validate_on_submit():
        tag_names = form.tag.data.split(",")  # get list of tags
        user = User.query.get(session['user_id'])
        author = user.username

        date_created = form.date_created.data  # date_created can be None

        if post:
            if form.title.data != post.title or form.content.data != post.content:
                post.date_updated = datetime.now()
            post.title = form.title.data
            post.content = form.content.data
            post.author = author
            post.date_created = date_created  # we always update date_created here
        else:
            post = Post(title=form.title.data,
                        content=form.content.data,
                        date_created=date_created,
                        date_posted=datetime.now(),
                        date_updated=datetime.now(),
                        author=author)
            db.session.add(post)

        # Clear existing tags before adding new ones
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

    elif request.method == 'GET' and post:
        form.title.data = post.title
        form.content.data = post.content
        form.tag.data = ', '.join(tag.name for tag in post.tags)
        form.date_created.data = post.date_created

    return render_template("manage_post.html", form=form, post=post)
