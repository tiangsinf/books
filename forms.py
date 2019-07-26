from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField(
        'Password', 
        validators=[
            DataRequired(),
            Length(min=3),
            EqualTo('Confirm Password')
        ]
    )
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Submit')