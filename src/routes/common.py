from src import app
from src.models import Album, Post, Tag, Page, User
from flask import render_template, render_template_string, redirect, url_for
from sqlalchemy import desc


@app.context_processor
def context_processor():
    excluded_titles = {"about", "contact", "subscribe", "donate", "rss", "home"}
    pages = (
        Page.query.filter(~Page.title.in_(excluded_titles)).order_by(Page.title).all()
    )
    site_name = app.config["SITE_NAME"]
    site_desc = app.config["SITE_DESC"]
    return dict(pages=pages, site_name=site_name, site_desc=site_desc)


@app.route("/<path:title>")
def page(title):
    page = Page.query.filter_by(title=title).first_or_404()
    posts = (
        Post.query.join(Post.tags)
        .filter(Tag.id.in_([tag.id for tag in page.related_tags]))
        .order_by(Post.date_posted.desc())
        .all()
    )
    tags_list = ",".join(tag.name for tag in page.related_tags)
    albums = Album.query.order_by(desc(Album.release_date)).all()
    content = render_template_string(
        page.content, posts=posts, tags_list=tags_list, albums=albums
    )
    return render_template(
        "page.html",
        page=page,
        posts=posts,
        tags_list=tags_list,
        albums=albums,
        content=content,
    )


@app.route("/music/album/<int:album_id>")
def view_album(album_id):
    album = Album.query.get(album_id)
    formatted_release_date = album.release_date.strftime("%d-%m-%Y")
    album.tracks.sort(
        key=lambda track: track.track_number
    )  # Sort tracks by track_number
    return render_template(
        "view_album.html", album=album, release_date=formatted_release_date
    )


@app.route("/user/<username>")
def view_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for("blog"))
    return render_template("view_user.html", user=user)


EMOTE_MAP = {
    ":wah:": "big-c.gif",
    ":eyebrows:": "eyebrows.gif",
    ":hah:": "hah.gif",
    ":loss:": "loss.gif",
    ":shock:": "shock.gif",
    ":laugh:": "big-laugh.gif",
    ":fangs:": "fangs.gif",
    ":happy:": "happy.gif",
    ":monocle:": "monocle.gif",
    ":smile:": "smile.gif",
    ":bleh:": "bleh.gif",
    ":fear:": "fear.gif",
    ":happyb:": "happy-plz.gif",
    ":nausea:": "nausea.gif",
    ":sponge:": "sponge.gif",
    ":concussed:": "concussed.gif",
    ":flat-smile:": "flat-smile.gif",
    ":shockb:": "harley-shock.gif",
    ":nosebleed:": "nosebleed.gif",
    ":super-smirk:": "super-smirk.gif",
    ":confounded:": "confounded.gif",
    ":flirty:": "flirty.gif",
    ":horror:": "horror.gif",
    ":not-impressed:": "not-impressed.gif",
    ":sweat:": "sweat.gif",
    ":confused:": "confused.gif",
    ":frown:": "frown.gif",
    ":icecream:": "jizz.gif",
    ":ohh:": "ohh.gif",
    ":intrigue:": "titty.gif",
    ":cringe:": "cringe.gif",
    ":gah:": "gah.gif",
    ":jolly:": "jolly.gif",
    ":snap:": "oh-snap.gif",
    ":of-course:": "tohru-kun.gif",
    ":disappoint:": "disappoint.gif",
    ":glad:": "glad.gif",
    ":joy:": "joy.gif",
    ":duh:": "patrick.gif",
    ":tongue:": "tongue.gif",
    ":eat-nose:": "eat-nose.gif",
    ":shockc:": "great-scott.gif",
    ":kawaii:": "kawaii.gif",
    ":rage:": "rage.gif",
    ":vein:": "vein.gif",
    ":egads:": "ee-gads.gif",
    ":grin:": "grin.gif",
    ":hehhh:": "konata.gif",
    ":raspberry:": "raspberry.gif",
    ":wut:": "wut.gif",
}


def replace_emotes(text):
    for code, filename in EMOTE_MAP.items():
        text = text.replace(
            code,
            f'<img src="{url_for("static", filename="emotes/" + filename)}" alt="{code}" class="emote">',
        )
    return text


app.jinja_env.filters["emotize"] = replace_emotes
