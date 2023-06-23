import os
from flask import Flask, render_template, abort, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))  # get the path to the directory of the current file
db_path = os.path.join(basedir, 'database.db')  # create a path that adds database.db to the end of the base directory path
db_uri = 'sqlite:///' + db_path  # create the full SQLite database URI

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    artist = db.Column(db.String(80), nullable=False)
    release_date = db.Column(db.String(80), nullable=False)
    cover_image = db.Column(db.String(120), nullable=True)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

API_KEY = "***REMOVED***"

@app.route('/')
def home():
    return render_template('home.html')

# Music
@app.route('/music')
def music():
    albums = Album.query.all()
    return render_template('music.html', albums=albums)

@app.route('/album/<int:id>')
def album(id):
    album = Album.query.get(id)
    if album is None:
        abort(404)  # Album not found
    return render_template('album.html', album=album)

# Blog
@app.route('/blog')
def blog():
    posts = BlogPost.query.all()
    return render_template("blog.html", posts=posts)

@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = BlogPost.query.get(post_id)
    if post:
        return render_template("view.html", post=post)
    else:
        return "Post not found", 404

@app.route("/add", methods=["GET", "POST"])
def add_post():
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_KEY:
        return "Unauthorized", 401

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        post = BlogPost(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html")

@app.route("/edit/<int:post_id>", methods=["GET", "PUT"])
def edit_post(post_id):
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_KEY:
        return "Unauthorized", 401

    post = BlogPost.query.get(post_id)
    if post:
        if request.method == "PUT":
            title = request.form["title"]
            content = request.form["content"]
            post.title = title
            post.content = content
            db.session.commit()
            return jsonify({"status": "success", "message": "Post updated"})
        return render_template("edit.html", post=post)
    else:
        return "Post not found", 404

@app.route("/delete/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_KEY:
        return "Unauthorized", 401

    post = BlogPost.query.get(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()
        return jsonify({"status": "success", "message": "Post deleted"})
    else:
        return "Post not found", 404

@app.route('/art')
def art():
    return render_template('art.html')

@app.route('/dev')
def dev():
    return render_template('dev.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)

