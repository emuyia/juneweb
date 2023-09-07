from src import app
from src.models import Post, Tag
from src.forms import SearchForm
from flask import render_template
from sqlalchemy import or_


@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get(post_id)
    return render_template("view_post.html", post=post)


@app.context_processor
def inject_search_form():
    return dict(search_form=SearchForm())


@app.route('/search/<query>', methods=['GET'])
def search_results(query):
    results = Post.query.filter(or_(Post.title.like("%" + query + "%"), Post.content.like("%" + query + "%"))).all()
    posts = Post.query.join(Post.tags).order_by(Post.date_posted.desc()).all()
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('search_results.html', query=query, results=results, posts=posts, tags=tags)
