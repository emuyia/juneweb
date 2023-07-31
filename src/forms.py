from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from src.models import Tag


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SubscriptionForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    tags = QuerySelectMultipleField('Tags', query_factory=lambda: Tag.query.all(),
                                    widget=ListWidget(html_tag='ul', prefix_label=False),
                                    option_widget=CheckboxInput())
    interval = SelectField('Summary Email Frequency', choices=[('daily', 'Daily'), ('weekly', 'Weekly'),
                                                               ('monthly', 'Monthly'), ('yearly', 'Yearly')])
    submit = SubmitField('Subscribe')
