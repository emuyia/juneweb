from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
import os

app = Flask(__name__)

app.config["SITE_NAME"] = os.environ.get("SITE_NAME", "website")
app.config["SITE_DESC"] = os.environ.get("SITE_DESC", "description")

app.config["ADMIN_USERNAME"] = os.environ.get("ADMIN_USERNAME", "admin")
app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD", "123")

app.config["SESSION_TYPE"] = os.environ.get("SESSION_TYPE", "filesystem")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "default_secret_key")
Session(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "SQLALCHEMY_DATABASE_URI"
) or "sqlite:///" + os.path.join(basedir, "database.db")
db = SQLAlchemy(app)

migrate = Migrate(app, db)

app.config["MAIL_API_KEY"] = os.environ.get("MAIL_API_KEY", "default_mail_api_key")
app.config["MAIL_GROUP_ID"] = os.environ.get("MAIL_GROUP_ID", "default_mail_group_id")

from src import routes, models
