from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask_mail import Mail
from src import config

app = Flask(__name__)

app.config["SESSION_TYPE"] = config.SESSION_TYPE
app.config["SECRET_KEY"] = config.SECRET_KEY
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

migrate = Migrate(app, db)

app.config['MAILCHIMP_DATACENTER'] = config.MAILCHIMP_DATACENTER
app.config['MAILCHIMP_API_KEY'] = config.MAILCHIMP_API_KEY
app.config['MAILCHIMP_LIST_ID'] = config.MAILCHIMP_LIST_ID

from src import routes, models
