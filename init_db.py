from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'albums.db')
db_uri = 'sqlite:///' + db_path

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

db = SQLAlchemy(app)

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    artist = db.Column(db.String(80), nullable=False)
    release_date = db.Column(db.String(80), nullable=False)
    cover_image = db.Column(db.String(120), nullable=True)

with app.app_context():
    db.create_all()

    new_album = Album(title="Album Title", artist="Artist Name", release_date="2023", cover_image="images/albums/test.jpg")
    db.session.add(new_album)
    new_album = Album(title="Another Album Title", artist="Artist Name", release_date="2024", cover_image="images/albums/test.jpg")
    db.session.add(new_album)

    db.session.commit()
