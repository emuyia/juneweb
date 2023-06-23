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

with app.app_context():
    db.drop_all()
    db.create_all()

    new_album = Album(title="Mahjong Hospital", artist="June", release_date="10th July 2023", cover_image="images/albums/mh.jpg")
    db.session.add(new_album)
    new_album = Album(title="Killy candy laura tell", artist="Daffodil", release_date="2nd September 2022", cover_image="images/albums/kclt.jpg")
    db.session.add(new_album)
    new_album = Album(title="The Eye", artist="Daffodil", release_date="2nd September 2022", cover_image="images/albums/te.jpg")
    db.session.add(new_album)
    new_album = Album(title="Leaden City", artist="Kiffter", release_date="13th May 2019", cover_image="images/albums/lc.jpg")
    db.session.add(new_album)
    new_album = Album(title="Poseidon's Kiss", artist="Kiffter", release_date="7th February 2019", cover_image="images/albums/pk.jpg")
    db.session.add(new_album)
    new_album = Album(title="Curdled", artist="Kiffter", release_date="22nd September 2018", cover_image="images/albums/curdled.jpg")
    db.session.add(new_album)
    new_album = Album(title="Ants In My Pants", artist="Atresed", release_date="20th August 2017", cover_image="images/albums/aimp.jpg")
    db.session.add(new_album)
    new_album = Album(title="Fruit Session", artist="Atresed", release_date="18th August 2017", cover_image="images/albums/fs.jpg")
    db.session.add(new_album)
    new_album = Album(title="Memes from the Multiverse", artist="Atresed & Tritric Acid", release_date="8th May 2017", cover_image="images/albums/mftm.jpg")
    db.session.add(new_album)
    new_album = Album(title="Small", artist="Atresed", release_date="1st December 2016", cover_image="images/albums/small.jpg")
    db.session.add(new_album)
    new_album = Album(title="Backward Gull", artist="Atresed", release_date="12th June 2016", cover_image="images/albums/bg.jpg")
    db.session.add(new_album)
    new_album = Album(title="Can Pears Introspect?", artist="Seven Frames", release_date="29th May 2015", cover_image="images/albums/cpi.jpg")
    db.session.add(new_album)
    new_album = Album(title="Oaulo", artist="Seven Frames", release_date="10th February 2015", cover_image="images/albums/oaulo.jpg")
    db.session.add(new_album)
    new_album = Album(title="Maodun", artist="Seven Frames", release_date="29th December 2014", cover_image="images/albums/maodun.jpg")
    db.session.add(new_album)

    new_blogpost = BlogPost(title="First Post", content="This is the first blog post")
    db.session.add(new_blogpost)

    db.session.commit()
