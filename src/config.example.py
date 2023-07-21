import os

SESSION_TYPE = "filesystem"
SECRET_KEY = "example"

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'example.db')

MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USERNAME = "email"
MAIL_PASSWORD = "password"
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_DEFAULT_SENDER = "email"

ADMIN_USERNAME = "admin"
