from src import app, db
from src.models import Album, Post, Tag, Page
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


@app.route("/page/<title>")
def page(title):
    page = Page.query.filter_by(title=title).first_or_404()
    posts = Post.query.join(Post.tags).filter(Tag.id.in_([tag.id for tag in page.related_tags])).order_by(Post.date_posted.desc()).all()
    tags_list = ','.join(tag.name for tag in page.related_tags)
    return render_template('page.html', page=page, posts=posts, tags_list=tags_list)


@app.route('/page_list')
def page_list():
    pages = Page.query.order_by(Page.title).all()
    return render_template('page_list.html', pages=pages)
