from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database.db')
db_uri = 'sqlite:///' + db_path

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

with app.app_context():
    db.drop_all()
    db.create_all()

    new_album = Album(title="Mahjong Hospital", artist="June", release_date="20230710", cover_image="images/albums/mh.jpg")
    db.session.add(new_album)
    new_album = Album(title="Killy candy laura tell", artist="Daffodil", release_date="20220902", cover_image="images/albums/kclt.jpg")
    db.session.add(new_album)
    new_album = Album(title="The Eye", artist="Daffodil", release_date="20201205", cover_image="images/albums/te.jpg")
    db.session.add(new_album)
    new_album = Album(title="Leaden City", artist="Kiffter", release_date="20190513", cover_image="images/albums/lc.jpg")
    db.session.add(new_album)
    new_album = Album(title="Poseidon's Kiss", artist="Kiffter", release_date="20190207", cover_image="images/albums/pk.jpg")
    db.session.add(new_album)
    new_album = Album(title="Curdled", artist="Kiffter", release_date="20180922", cover_image="images/albums/curdled.jpg")
    db.session.add(new_album)
    new_album = Album(title="Ants In My Pants", artist="Atresed", release_date="20170820", cover_image="images/albums/aimp.jpg")
    db.session.add(new_album)
    new_album = Album(title="Fruit Session", artist="Atresed", release_date="20170818", cover_image="images/albums/fs.jpg")
    db.session.add(new_album)
    new_album = Album(title="Memes from the Multiverse", artist="Atresed & Tritric Acid", release_date="20170508", cover_image="images/albums/mftm.jpg")
    db.session.add(new_album)
    new_album = Album(title="Small", artist="Atresed", release_date="20161201", cover_image="images/albums/small.jpg")
    db.session.add(new_album)
    new_album = Album(title="Backward Gull", artist="Atresed", release_date="20160612", cover_image="images/albums/bg.jpg")
    db.session.add(new_album)
    new_album = Album(title="Can Pears Introspect?", artist="Seven Frames", release_date="20150529", cover_image="images/albums/cpi.jpg")
    db.session.add(new_album)
    new_album = Album(title="Oaulo", artist="Seven Frames", release_date="20150210", cover_image="images/albums/oaulo.jpg")
    db.session.add(new_album)
    new_album = Album(title="Maodun", artist="Seven Frames", release_date="20141229", cover_image="images/albums/maodun.jpg")
    db.session.add(new_album)

    new_blogpost = BlogPost(title="First Post", content="This is the first blog post")
    db.session.add(new_blogpost)

    # admin_user = User(username="june", password="***REMOVED***", is_admin=True)
    # db.session.add(admin_user)

    db.session.commit()
