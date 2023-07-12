from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session

from src import config

app = Flask(__name__)

app.config["SESSION_TYPE"] = config.SESSION_TYPE
app.config["SECRET_KEY"] = config.SECRET_KEY
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

migrate = Migrate(app, db)

from src import routes, models
