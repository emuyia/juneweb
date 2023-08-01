from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from src.models import Tag
from datetime import datetime


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class OptionalDateField(DateField):
    def process_formdata(self, valuelist):
        if valuelist:
            if valuelist[0] == '':
                self.data = None  # set to None if no date is provided
            else:
                super(OptionalDateField, self).process_formdata(valuelist)
        else:
            self.data = None


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    tag = StringField('Tags')
    date_created = OptionalDateField('Date Created')
    submit = SubmitField('Submit')
