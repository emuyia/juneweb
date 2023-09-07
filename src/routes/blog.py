from src import app, db
from src.models import Post, Tag, User
from src.forms import PostForm, SearchForm
from src.routes.auth import admin_required
from flask import render_template, request, redirect, url_for, session
from sqlalchemy import func, or_
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
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

    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(url_for('search_results', query=search_form.query.data))

    return render_template("blog.html", posts=posts, tags=tags, selected_tags=selected_tags or [],
                           search_form=search_form)


@app.context_processor
def inject_search_form():
    return dict(search_form=SearchForm())


@app.route('/search/<query>', methods=['GET'])
def search_results(query):
    results = Post.query.filter(or_(Post.title.like("%" + query + "%"), Post.content.like("%" + query + "%"))).all()
    posts = Post.query.join(Post.tags).order_by(Post.date_posted.desc()).all()
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('search_results.html', query=query, results=results, posts=posts, tags=tags)


@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get(post_id)
    return render_template("view_post.html", post=post)
