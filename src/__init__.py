from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
import os
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect, generate_csrf

load_dotenv()

app = Flask(__name__)

csrf = CSRFProtect(app)

app.config["SITE_NAME"] = os.environ.get("SITE_NAME", "website")
app.config["SITE_DESC"] = os.environ.get("SITE_DESC", "description")

app.config["DOMAIN"] = os.environ.get("DOMAIN", "domain")

app.config["ADMIN_USERNAME"] = os.environ.get("ADMIN_USERNAME", "admin")
app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD", "123")

app.config["SESSION_TYPE"] = os.environ.get("SESSION_TYPE", "filesystem")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "default_secret_key")
Session(app)

app.config["SECURITY_PASSWORD_SALT"] = os.environ.get(
    "SECURITY_PASSWORD_SALT", "default_salt"
)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri or "sqlite:///" + os.path.join(
    basedir, "database.db"
)
db = SQLAlchemy(app)

migrate = Migrate(app, db)

app.config["MAILERLITE_API_KEY"] = os.environ.get(
    "MAILERLITE_API_KEY", "default_mailerlite_api_key"
)
app.config["MAILERLITE_GROUP_ID"] = os.environ.get(
    "MAILERLITE_GROUP_ID", "default_mailerlite_group_id"
)
app.config["MAILERSEND_API_KEY"] = os.environ.get(
    "MAILERSEND_API_KEY", "default_mailersend_api_key"
)

app.config["MUSIC_ARCHIVE_CDN"] = os.environ.get("MUSIC_ARCHIVE_CDN", "default")

from src import routes, models
