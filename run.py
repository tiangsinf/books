import os

from flask import Flask, session, render_template, redirect, url_for, request, abort, Response
from flask_session import Session
from dotenv import load_dotenv
from config import config

load_dotenv()
app = Flask(__name__)
app.config.from_object(config['development'])

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

Session(app)

from models import *
@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User)

from forms import LoginForm, RegistrationForm
@app.route('/')
def goto_login():
    if session['SESSIONUSER'] is None:
        return redirect(url_for('login'))
    
    return redirect(url_for('books'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # When user submits form
    if form.validate_on_submit():

        # Record keyed in email and password to session
        session['loginer'] = form.email.data # To replace html placeholder when email is submitted

        session.pop('not_registered', None)
        session.pop('wrong_password', None)

        # Get user by email
        user = User.query.filter_by(email = form.email.data).scalar()
        
        # If user (email) does not exist:
        if user is None:
            session.pop('password', None)

            session['not_registered'] = True
            return redirect('login')

        # If user (email) is found but password not matched:
        elif user.password != form.password.data:
            session.pop('password', None)

            session['wrong_password'] = True
            return redirect('login')
        
        # All matched
        else:
            # Set user to session user:
            session['SESSIONUSER'] = user
            return redirect(url_for('books')) 
    
    return render_template(
        'login.html', 
        form = form, 
        not_registered = session.get('not_registered'), 
        wrong_password = session.get('wrong_password')
    )

@app.route('/books')
def books():
    if session['SESSIONUSER'] is None:
        return redirect(url_for('login'))

    return render_template('books.html', user = session.get('SESSIONUSER'))

@app.route('/logout/')
def logout():
    session.pop('SESSIONUSER', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()