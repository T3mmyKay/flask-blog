from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(message="Email is required")])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField(label="Login")
