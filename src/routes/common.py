from src import app, db
from src.models import Album, Post, Tag, Page, User
from flask import render_template, render_template_string, request, redirect, url_for, flash
from sqlalchemy import desc, func


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
    return render_template("blog.html", posts=posts, tags=tags, selected_tags=selected_tags or [])


@app.route('/<path:title>')
def page(title):
    page = Page.query.filter_by(title=title).first_or_404()
    posts = Post.query.join(Post.tags).filter(Tag.id.in_([tag.id for tag in page.related_tags])).order_by(Post.date_posted.desc()).all()
    tags_list = ','.join(tag.name for tag in page.related_tags)
    albums = Album.query.order_by(desc(Album.release_date)).limit(4).all()
    content = render_template_string(page.content, posts=posts, tags_list=tags_list, albums=albums)
    return render_template('page.html', page=page, posts=posts, tags_list=tags_list, albums=albums, content=content)


@app.route('/page_list')
def page_list():
    pages = Page.query.order_by(Page.title).all()
    return render_template('page_list.html', pages=pages)


@app.route('/music/album/<int:album_id>')
def view_album(album_id):
    album = Album.query.get(album_id)
    formatted_release_date = album.release_date.strftime('%d-%m-%Y')
    album.tracks.sort(key=lambda track: track.track_number)  # Sort tracks by track_number
    return render_template('view_album.html', album=album, release_date=formatted_release_date)


@app.route('/user/<username>')
def view_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        # Handle case where no user with the provided username exists
        flash('User not found.', 'error')
        return redirect(url_for('blog'))
    return render_template('view_user.html', user=user)


@app.route('/contact')
def contact():
    return render_template('contact.html')
