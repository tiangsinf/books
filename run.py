import os

from flask import Flask, session, render_template, redirect, url_for, request
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
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit() is True: 
        # write to session (key : value pairs) 
        session['email'] = form.email.data 
        session['password'] = form.password.data
        return redirect(url_for('index'))
    # post/redirect/get
    return render_template('login.html', form=form, 
                        email=session.get('email'), 
                        password=session.get('password'))

@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if 'email' in session:
        email = session.get('email')
    
    if form.validate_on_submit() is True:
        session['name'] = form.name.data
        session['email'] = form.email.data
        session['password'] = form.password.data
        return redirect(url_for('register'))


    return render_template('register.html', form=form, 
                        name=session.get('name'),
                        email=session.get('email'),
                        password=session.get('password'))

@app.route('/logout/')
def logout():
    session.pop('email')
    session.pop('name')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()