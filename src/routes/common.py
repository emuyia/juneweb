from src import app
from src.routes import wd_wdb, auth
from src.models import Post, Tag, Page, User
from flask import (
    render_template,
    render_template_string,
    redirect,
    url_for,
    jsonify,
    request,
)
import requests


@app.context_processor
def context_processor():
    pages = Page.query.filter_by(hidden=False).order_by(Page.title).all()
    site_name = app.config["SITE_NAME"]
    site_desc = app.config["SITE_DESC"]
    return dict(
        pages=pages,
        site_name=site_name,
        site_desc=site_desc,
        get_role_nick=auth.get_role_nick,
    )


@app.route("/<path:title>")
def page(title):
    page = Page.query.filter_by(title=title).first_or_404()
    wd_langtable_item = None
    wd_langtable_file = wd_wdb.langtable_file
    wd_documents = None

    # Check for unique page features
    if title == "white-day/langtable-search":
        search_id = request.args.get("search_id")
        if search_id:
            wd_langtable_item = wd_wdb.process_langtable_search(search_id)
    if title == "white-day/documents":
        wd_documents = wd_wdb.get_documents()

    redirect_url = page.redirect_url
    if redirect_url is not None:
        return redirect(redirect_url, code=302)

    posts = (
        Post.query.join(Post.tags)
        .filter(Tag.id.in_([tag.id for tag in page.related_tags]))
        .order_by(Post.date_posted.desc())
        .all()
    )
    tags_list = ",".join(tag.name for tag in page.related_tags)

    content = render_template_string(
        page.content,
        posts=posts,
        tags_list=tags_list,
        langtable_item=wd_langtable_item,
        langtable_file=wd_langtable_file,
        documents=wd_documents,
    )
    return render_template(
        "page.html",
        page=page,
        posts=posts,
        tags_list=tags_list,
        content=content,
        langtable_item=wd_langtable_item,
        langtable_file=wd_langtable_file,
        documents=wd_documents,
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


@app.route("/emotes.json")
def emotes_json():
    return jsonify(EMOTE_MAP)


def exists(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


app.jinja_env.tests["exists"] = exists
