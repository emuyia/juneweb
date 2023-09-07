from src import app, db
from src.models import Album, Post, Tag, Page
from flask import render_template, render_template_string, request, redirect, url_for
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

    '''
    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(url_for('search_results', query=search_form.query.data))
    '''

    # return render_template("blog.html", posts=posts, tags=tags, selected_tags=selected_tags or [],
    #                        search_form=search_form)
    return render_template("blog.html", posts=posts, tags=tags, selected_tags=selected_tags or [])


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/<title>")
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


@app.route('/music/discog')
def discog():
    albums = Album.query.order_by(desc(Album.release_date)).all()
    return render_template('discog.html', albums=albums)


@app.route("/music/album/<int:album_id>")
def view_album(album_id):
    album = Album.query.get(album_id)
    formatted_release_date = album.release_date.strftime("%d-%m-%Y")
    album.tracks.sort(key=lambda track: track.track_number)  # Sort tracks by track_number
    return render_template("view_album.html", album=album, release_date=formatted_release_date)
