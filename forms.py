from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
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
            Length(min=3)
        ]
    )
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo(password, message='Password must match!')])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    isbn = StringField('Search by ISBN No.')
    title = StringField("Search by Book's Title")
    author = StringField("Search by Author's Name")
    year = StringField('Year')
    submit = SubmitField('Search')

class ReviewForm(FlaskForm):
    review = TextAreaField('What do you think...', validators = [DataRequired()])
    rating = SelectField(
        'Your Rating',
        choices = [
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5)
        ],
        validators = [DataRequired()]
    )
    submit = SubmitField('Submit')