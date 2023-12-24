import os

SITE_NAME = "website"
SITE_DESC = "description"

SESSION_TYPE = "filesystem"
SECRET_KEY = "example"

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "example.db")

MAIL_API_KEY = "your_api_key"
MAIL_GROUP_ID = "your_group_id"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123"
