from src import app, db
from src.models import Post, Comment
from flask import render_template, request, flash, redirect, url_for, Response, abort
import requests
from feedgen.feed import FeedGenerator
import pytz
from flask_login import login_required, current_user
from datetime import datetime as dt
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import MultifieldParser, OrGroup
from sqlalchemy import event
from apscheduler.schedulers.background import BackgroundScheduler


@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get(post_id)
    if post.date_updated is None:
        post.date_updated = post.date_posted
    return render_template("view_post.html", post=post)


schema = Schema(
    id=ID(stored=True),
    title=TEXT(stored=True),
    content=TEXT(stored=True),
    date_posted=DATETIME(stored=True, sortable=True),
    tags=KEYWORD(stored=True, commas=True)
)

index_dir = 'whoosh_index'
index = create_in(index_dir, schema)


def index_posts():
    writer = index.writer()
    for post in Post.query.all():
        writer.add_document(
            id=str(post.id),
            title=post.title,
            content=post.content,
            date_posted=post.date_posted,
            tags=post.get_tags()
        )
    writer.commit()


with app.app_context():
    index_posts()


def add_to_index(mapper, connection, post):
    writer = index.writer()
    writer.add_document(
        id=str(post.id),
        title=post.title,
        content=post.content,
        date_posted=post.date_posted,
        tags=post.get_tags()
    )
    writer.commit()


def remove_from_index(mapper, connection, post):
    writer = index.writer()
    writer.delete_by_term('id', str(post.id))
    writer.commit()


def update_index(mapper, connection, post):
    remove_from_index(mapper, connection, post)
    add_to_index(mapper, connection, post)


event.listen(Post, 'after_insert', add_to_index)
event.listen(Post, 'after_update', update_index)
event.listen(Post, 'after_delete', remove_from_index)


searcher = index.searcher()


def refresh_searcher():
    global searcher
    searcher = searcher.refresh()


scheduler = BackgroundScheduler()
scheduler.add_job(refresh_searcher, 'interval', minutes=1)
scheduler.start()


@app.route("/search")
def search():
    query = request.args.get('q', '')
    post_ids = []
    if query:
        global searcher
        og = OrGroup.factory(0.9)
        query = MultifieldParser(["title", "content", "tags"], index.schema, group=og).parse(query)
        results = searcher.search(query)
        for hit in results:
            post_ids.append(hit['id'])
    posts = Post.get_posts_by_ids(post_ids)
    return render_template('search.html', posts=posts, query=query)


@app.route('/submit_comment', methods=['POST'])
@login_required
def submit_comment():
    post_id = request.form.get('post_id')
    content = request.form.get('content')
    new_comment = Comment(content=content, post_id=post_id, author_id=current_user.id, date_posted=dt.now())
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('view_post', post_id=post_id))


@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if comment.author != current_user:
        abort(403)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    # flash('Your comment has been deleted!', 'success')
    return redirect(url_for('view_post', post_id=post_id))


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    api_key = app.config['MAIL_API_KEY']
    headers = {
        'Content-Type': 'application/json',
        'X-MailerLite-ApiKey': api_key,
    }
    if request.method == 'POST':
        email = request.form['email']
        if 'unsubscribe' in request.form:
            # Unsubscribe Logic
            response = requests.get(f'https://api.mailerlite.com/api/v2/subscribers/{email}', headers=headers)
            if response.status_code == 200:
                subscriber_id = response.json()['id']
                group_id = app.config['MAIL_GROUP_ID']
                response = (requests.delete
                            (f'https://api.mailerlite.com/api/v2/groups/{group_id}/subscribers/{subscriber_id}',
                             headers=headers))
                if response.status_code == 200 or response.status_code == 204:
                    flash('Unsubscribed successfully')
                    return redirect(url_for('subscribe'))
                else:
                    flash('Error unsubscribing')
                    print(f"Unsubscribe failed with status {response.status_code}: {response.content}")
            else:
                flash('Error finding subscriber')
                print(f"Subscriber retrieval failed with status {response.status_code}: {response.content}")
        elif 'subscribe' in request.form:
            # Subscribe Logic
            group_id = app.config['MAIL_GROUP_ID']
            response = requests.post(f'https://api.mailerlite.com/api/v2/groups/{group_id}/subscribers',
                                     headers=headers, json={'email': email})
            if response.status_code == 200:
                flash('Subscribed successfully')
                return redirect(url_for('subscribe'))
            else:
                flash('Error subscribing')
                print(f"Subscribe failed with status {response.status_code}: {response.content}")
    return render_template('subscribe.html')


@app.route('/feed')
def feed():
    fg = FeedGenerator()
    fg.title(app.config['SITE_NAME'])
    fg.link(href=request.url_root)
    fg.description(app.config['SITE_DESC'])

    posts = Post.query.order_by(Post.date_posted.desc()).all()
    for post in posts:
        fe = fg.add_entry()
        fe.title(post.title)
        fe.link(href=f"{request.url_root}post/{post.id}")
        fe.description(post.content)
        fe.pubDate(post.date_posted.replace(tzinfo=pytz.timezone('Europe/London')))
        fe.author(name=post.author.username)

    response = fg.rss_str(pretty=True)
    return Response(response, mimetype='application/rss+xml')
