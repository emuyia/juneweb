import os

SESSION_TYPE = "filesystem"
SECRET_KEY = "example"

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'example.db')

MAILCHIMP_DATACENTER = 'usX'
MAILCHIMP_API_KEY = 'your_api_key'
MAILCHIMP_LIST_ID = 'your_list_id'
MAILCHIMP_CAMPAIGN_ID = 'your_campaign_id'

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123"
