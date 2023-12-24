from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask_mail import Mail
from src import config

app = Flask(__name__)

app.config["SITE_NAME"] = config.SITE_NAME
app.config["SITE_DESC"] = config.SITE_DESC

app.config["SESSION_TYPE"] = config.SESSION_TYPE
app.config["SECRET_KEY"] = config.SECRET_KEY
Session(app)

app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

migrate = Migrate(app, db)

app.config["MAIL_API_KEY"] = config.MAIL_API_KEY
app.config["MAIL_GROUP_ID"] = config.MAIL_GROUP_ID

from src import routes, models
