from src import app, db
from src.models import Album, Post, Tag
from src.routes.auth import admin_required
from flask import redirect, url_for, render_template


@app.route("/delete_item/<item_type>/<int:item_id>", methods=["POST"])
@admin_required
def delete_item(item_type, item_id):
    print(f"delete_item({item_type}, {item_id}")
    item = None
    if item_type == 'post':
        item = Post.query.get(item_id)
    elif item_type == 'album':
        item = Album.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    else:
        return redirect(url_for('blog'))
    return redirect(url_for('blog'))


@app.route("/about")
def about():
    return render_template('about.html')


@app.route('/dev')
def dev():
    posts = Post.query.join(Post.tags).filter(Tag.name == 'dev').order_by(Post.date_posted.desc()).all()
    tags = Tag.query.order_by(Tag.name).all()
    return render_template("dev.html", posts=posts, tags=tags)
