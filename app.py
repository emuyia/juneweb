import os
from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))  # get the path to the directory of the current file
db_path = os.path.join(basedir, 'albums.db')  # create a path that adds albums.db to the end of the base directory path
db_uri = 'sqlite:///' + db_path  # create the full SQLite database URI

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    artist = db.Column(db.String(80), nullable=False)
    release_date = db.Column(db.String(80), nullable=False)
    cover_image = db.Column(db.String(120), nullable=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/album/<int:id>')
def album(id):
    album = Album.query.get(id)
    if album is None:
        abort(404)  # Album not found
    return render_template('album.html', album=album)

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/music')
def music():
    albums = Album.query.all()
    return render_template('music.html', albums=albums)

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

