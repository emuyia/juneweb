from src import app, db
from src.models import Post, Comment, User, Tag
from src.routes.common import EMOTE_MAP
from flask import render_template, request, flash, url_for, Response, abort, redirect
from feedgen.feed import FeedGenerator
import pytz
from flask_login import login_required, current_user
from datetime import datetime, timezone
from whoosh.index import create_in
from whoosh.fields import Schema, ID, TEXT, DATETIME, KEYWORD, re
from whoosh.qparser import MultifieldParser, OrGroup
from sqlalchemy import event, func
from apscheduler.schedulers.background import BackgroundScheduler
from bleach import clean, linkify
from bs4 import BeautifulSoup
import os
from flask_wtf.csrf import CSRFProtect
from markdown import markdown


csrf = CSRFProtect(app)


@app.route("/", methods=["GET", "POST"])
def blog():
    selected_tags = request.args.get("tags")
    page = request.args.get("page", 1, type=int)
    posts_per_page = 12  # Number of posts per page.
    posts = Post.query.filter_by(status='published')

    if selected_tags:
        selected_tags = selected_tags.split(",")
        subquery = (
            db.session.query(Post.id)
            .join(Post.tags)
            .filter(Tag.name.in_(selected_tags), Post.status == 'published')
            .group_by(Post.id)
            .having(func.count(Tag.id) == len(selected_tags))
            .subquery()
        )
        posts = posts.filter(Post.id.in_(subquery))

    pagination = posts.order_by(Post.date_posted.desc()).paginate(
        page=page, per_page=posts_per_page, error_out=False
    )

    tags = Tag.query.order_by(Tag.name).all()

    return render_template(
        "blog.html", pagination=pagination, tags=tags, selected_tags=selected_tags or []
    )


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    if not current_user.has_role('Admin'):
        flash('You do not have permission to create posts.', 'danger')
        return redirect(url_for('blog'))

    if request.method == 'POST':
        title = request.form['title']
        content_md = request.form['content']  # Retrieve the Markdown content from the form
        status = request.form.get('status', 'draft')

        # Convert Markdown to HTML using `markdown` library
        content_html = markdown(content_md, extensions=['fenced_code', 'codehilite'])

        # Sanitize the HTML content
        cleaned_content = clean(
            content_html,
            tags=['p', 'strong', 'em', 'blockquote', 'code', 'pre', 'ul', 'ol', 'li', 'a',
                  'h1', 'h2', 'h3', 'img', 'hr', 'br', 'table', 'thead', 'tbody', 'tr', 'th', 'td'],
            attributes={
                'a': ['href', 'title', 'target'],
                'img': ['src', 'alt', 'title', 'width', 'height'],
                'code': ['class'],
            },
            strip=True
        )

        new_post = Post(
            title=title,
            content_md=content_md,  # Store the original Markdown content
            content=cleaned_content,  # Store the sanitized HTML content
            status=status,
            author_id=current_user.id,
            date_posted=datetime.now(timezone.utc)
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Post saved successfully.', 'success')
        return redirect(url_for('view_post', post_id=new_post.id))

    return render_template('create_post.html', emote_map=EMOTE_MAP)


@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author_id != current_user.id and not current_user.has_role('Admin'):
        flash('You do not have permission to edit this post.', 'danger')
        return redirect(url_for('view_post', post_id=post.id))

    if request.method == 'POST':
        post.title = request.form['title']
        content_md = request.form['content']
        status = request.form.get('status', 'draft')

        # Convert Markdown to HTML
        content_html = markdown(content_md, extensions=['fenced_code', 'codehilite'])

        # Sanitize the HTML content
        cleaned_content = clean(
            content_html,
            tags=['p', 'strong', 'em', 'blockquote', 'code', 'pre', 'ul', 'ol', 'li', 'a',
                  'h1', 'h2', 'h3', 'img', 'hr', 'br', 'table', 'thead', 'tbody', 'tr', 'th', 'td'],
            attributes={
                'a': ['href', 'title', 'target'],
                'img': ['src', 'alt', 'title', 'width', 'height'],
                'code': ['class'],
            },
            strip=True
        )

        # Update the post with new content
        post.content_md = content_md  # Update the Markdown content
        post.content = cleaned_content  # Update the sanitized HTML content
        post.status = status
        db.session.commit()
        flash('Post updated successfully.', 'success')
        return redirect(url_for('view_post', post_id=post.id))

    return render_template('edit_post.html', post=post, emote_map=EMOTE_MAP)


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author_id != current_user.id and not current_user.has_role('Admin'):
        flash('You do not have permission to delete this post.', 'danger')
        return redirect(url_for('view_post', post_id=post.id))

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully.', 'success')
    return redirect(url_for('blog'))


@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.status != 'published':
        if not current_user.is_authenticated or (post.author_id != current_user.id and not current_user.has_role('Admin')):
            flash('You do not have permission to view this post.', 'danger')
            return redirect(url_for('blog'))
    if post.date_updated is None:
        post.date_updated = post.date_posted
    for comment in post.comments:
        comment.content = process_comment(comment.content)
    return render_template("view_post.html", post=post, emote_map=EMOTE_MAP)


def process_comment(comment_text):
    # Remove all HTML tags
    sanitized_text = clean(comment_text, tags=[], strip=True)

    # Linkify URLs
    comment_text = linkify(sanitized_text)

    # Add target="_blank" to <a> tags
    soup = BeautifulSoup(comment_text, features="html.parser")
    for a in soup.findAll("a"):
        a["target"] = "_blank"
    comment_text = str(soup)

    # matches @ followed by one or more characters or underscores, except if preceded by backslash
    pattern = r"(?<!\\)@(\w+)"

    # replace @username with link to user's profile page if user exists
    def replace_username_with_link(match):
        username = match.group(1).lower()
        user = User.query.filter(func.lower(User.username) == username.lower()).first()
        if user is not None:
            return f'<a href="{url_for("view_user", username=user.username)}" target="_blank">@{user.nickname.upper()}</a>'
        else:
            return f"@{username}".upper()

    comment_text = re.sub(pattern, replace_username_with_link, comment_text)

    # Remove backslashes preceding a @
    comment_text = re.sub(r"\\@", "@", comment_text)

    return comment_text


@app.route("/submit_comment", methods=["POST"])
def submit_comment():
    post_id = request.form.get("post_id")
    content = request.form.get("content")

    if not current_user.is_authenticated:
        flash("You need to be logged in to submit comments.", "warning")
        return redirect(url_for("view_post", post_id=post_id))

    new_comment = Comment(
        content=content,
        post_id=post_id,
        author_id=current_user.id,
        date_posted=datetime.now(timezone.utc),
    )

    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for("view_post", post_id=post_id))


@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if comment.author != current_user:
        abort(403)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for("view_post", post_id=post_id))


@app.route("/comment/edit/<int:comment_id>", methods=["GET"])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if comment.author.id != current_user.id:
        flash("You cannot edit someone else's comment.")
        return redirect(url_for("view_post", post_id=comment.post.id))
    return render_template("edit_comment.html", comment=comment, emote_map=EMOTE_MAP)


@app.route("/comment/edit/<int:comment_id>", methods=["POST"])
@login_required
def submit_edited_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if comment.author.id != current_user.id:
        return redirect(url_for("view_post", post_id=comment.post.id))
    comment.content = request.form["content"]
    db.session.commit()
    return redirect(url_for("view_post", post_id=comment.post.id))


schema = Schema(
    id=ID(stored=True),
    title=TEXT(stored=True),
    content=TEXT(stored=True),
    date_posted=DATETIME(stored=True, sortable=True),
    tags=KEYWORD(stored=True, commas=True),
)

index_dir = "whoosh_index"

if not os.path.exists(index_dir):
    os.makedirs(index_dir)

index = create_in(index_dir, schema)


def index_posts():
    with app.app_context():
        writer = index.writer()
        for post in Post.query.filter_by(status='published').all():
            writer.add_document(
                id=str(post.id),
                title=post.title,
                content=post.content,
                date_posted=post.date_posted,
                tags=post.get_tags(),
            )
        writer.commit()


def add_to_index(mapper, connection, post):
    if post.status == 'published':
        writer = index.writer()
        writer.add_document(
            id=str(post.id),
            title=post.title,
            content=post.content,
            date_posted=post.date_posted,
            tags=post.get_tags(),
        )
        writer.commit()


def remove_from_index(mapper, connection, post):
    writer = index.writer()
    writer.delete_by_term("id", str(post.id))
    writer.commit()


def update_index(mapper, connection, post):
    remove_from_index(mapper, connection, post)
    if post.status == 'published':
        add_to_index(mapper, connection, post)


event.listen(Post, "after_insert", add_to_index)
event.listen(Post, "after_update", update_index)
event.listen(Post, "after_delete", remove_from_index)


searcher = index.searcher()


def refresh_searcher():
    global searcher
    searcher = searcher.refresh()


scheduler = BackgroundScheduler()
scheduler.add_job(refresh_searcher, "interval", minutes=1)
scheduler.start()


@app.route("/search")
def search():
    query = request.args.get("q", "")
    post_ids = []
    if query:
        global searcher
        og = OrGroup.factory(0.9)
        query = MultifieldParser(
            ["title", "content", "tags"], index.schema, group=og
        ).parse(query)
        results = searcher.search(query)
        for hit in results:
            post_ids.append(hit["id"])
    posts = Post.get_posts_by_ids(post_ids)
    return render_template("search.html", posts=posts, query=query)


@app.route("/feed")
def feed():
    fg = FeedGenerator()
    fg.title(app.config["SITE_NAME"])
    fg.link(href=request.url_root)
    fg.description(app.config["SITE_DESC"])

    posts = Post.query.order_by(Post.date_posted.desc()).all()
    for post in posts:
        fe = fg.add_entry()
        fe.title(post.title)
        fe.link(href=f"{request.url_root}post/{post.id}")
        fe.description(post.content)
        fe.pubDate(post.date_posted.replace(tzinfo=pytz.timezone("Europe/London")))
        fe.author(name=post.author.username)

    response = fg.rss_str(pretty=True)
    return Response(response, mimetype="application/rss+xml")


@app.route('/my_posts')
@login_required
def my_posts():
    drafts = Post.query.filter_by(author_id=current_user.id, status='draft').all()
    published = Post.query.filter_by(author_id=current_user.id, status='published').all()
    return render_template('my_posts.html', drafts=drafts, published=published)
