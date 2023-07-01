import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from flask_session import Session

app = Flask(__name__)

app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "***REMOVED***"
Session(app)

basedir = os.path.abspath(os.path.dirname(__file__))  # get the path to the directory of the current file
db_path = os.path.join(basedir, 'database.db')  # create a path that adds database.db to the end of the base dir path
db_uri = 'sqlite:///' + db_path  # create the full SQLite database URI

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    artist = db.Column(db.String(80), nullable=False)
    release_date = db.Column(db.String(80), nullable=False)
    cover_image = db.Column(db.String(120), nullable=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


@app.context_processor
def context_processor():
    user = None
    is_admin = False

    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user:
            is_admin = user.is_admin

    return {"user": user, "check_if_admin": lambda: is_admin}


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        is_admin = True if username == "june" else False
        user = User(username=username, password=password, is_admin=is_admin)
        db.session.add(user)
        db.session.commit()
        session["username"] = username
        return redirect(url_for("home"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Logged in successfully.", "success")
            print("Logged in successfully.")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "error")
    return render_template("login.html")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You need to login first.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You need to login first.", "error")
            return redirect(url_for("login"))
        user = User.query.get(session["user_id"])
        if not user.is_admin:
            flash("You do not have access to this page.", "error")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function


def check_if_admin():
    if 'user' in session:
        user = User.query.get(session['user_id'])
        return user.is_admin
    return False


@app.route("/profile", methods=["GET", "POST"])
def profile():
    #
    return redirect(url_for("profile"))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/blog')
def blog():
    print("blog")
    posts = BlogPost.query.all()
    return render_template("blog.html", posts=posts)


@app.route('/music')
def music():
    albums = Album.query.order_by(Album.release_date).all()
    return render_template('music.html', albums=albums)


@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = BlogPost.query.get(post_id)
    return render_template("view_post.html", post=post)


@app.route("/album/<int:album_id>")
def view_album(album_id):
    album = Album.query.get(album_id)
    return render_template("view_album.html", album=album)


@app.route("/add_post", methods=["GET", "POST"])
@app.route("/edit_post/<int:post_id>", methods=["GET", "POST"])
@admin_required
def manage_post(post_id=None):
    post = None
    if post_id:
        post = BlogPost.query.get(post_id)
    if request.method in ["POST", "PUT"]:
        title = request.form["title"]
        content = request.form["content"]
        if post:
            post.title = title
            post.content = content
        else:
            post = BlogPost(title=title, content=content)
            db.session.add(post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("manage_post.html", post=post)


@app.route("/add_album", methods=["GET", "POST"])
@app.route("/edit_album/<int:album_id>", methods=["GET", "POST"])
@admin_required
def manage_album(album_id=None):
    album = None
    if album_id:
        album = Album.query.get(album_id)
    if request.method in ["POST", "PUT"]:
        title = request.form["title"]
        artist = request.form["artist"]
        release_date = request.form["release_date"]
        cover_image = request.form["cover_image"]
        if album:
            album.name = title
            album.artist = artist
            album.release_date = release_date
            album.cover_image = cover_image
        else:
            album = Album(title=title, artist=artist, release_date=release_date, cover_image=cover_image)
            db.session.add(album)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("manage_album.html", album=album)


@app.route("/delete_item/<item_type>/<int:item_id>", methods=["POST"])
@admin_required
def delete_item(item_type, item_id):
    print(f"delete_item({item_type}, {item_id}")
    item = None
    if item_type == 'post':
        item = BlogPost.query.get(item_id)
    elif item_type == 'album':
        item = Album.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    else:
        print('Item not found', 'error')
        return redirect(url_for('home'))
    print('Item deleted successfully', 'success')
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
