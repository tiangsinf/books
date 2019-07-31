# 0.0 IMPORT REQUIRED PACKAGES
import os

from flask import Flask, session, render_template, redirect, url_for, request, abort, Response
from flask_session import Session
from dotenv import load_dotenv
from config import config

# 0.1 LOAD ENVIRONMENTS
load_dotenv()

# 0.2 INITIATE APP FROM CONFIG
app = Flask(__name__)
app.config.from_object(config['development'])

Session(app)

# 0.3 CHECK ENV:
if not os.getenv('DATABASE_URL'):
    raise RuntimeError('DATABASE_URL is not set')
if not os.getenv('FLASK_APP'):
    raise RuntimeError('FLASK_APP is not set')

# 0.4 MAKE CONTEXT PROCESSOR
from models import *
@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Book=Book)

# 1.0 HOME ROUTE
# user not logged in
from forms import LoginForm, RegistrationForm, SearchForm
@app.route('/')
def goto_login():
    return redirect(url_for('books'))

# 2.0 GET USER LOGIN
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

# 2.1 LOGOUT
@app.route('/logout/')
def logout():

    # clear user session
    session.pop('SESSIONUSER', None)
    return redirect(url_for('login'))

# 2.2 REGISTRATION FOR NEW USER
@app.route('/register', methods=['GET', 'POST'])
def register():

    # render registration form
    form = RegistrationForm()
    
    if request.method == 'POST':
        session['name'] = form.name.data
        session['email'] = form.email.data
        session['password'] = form.password.data

        # Check if email exist:
        user = User.query.filter_by(email=session.get('email')).scalar()

        # Allow user to register
        if user is None:
            new_user = User(session.get('name'), session.get('email'), session.get('password'))
            db.session.add(new_user)
            db.session.commit()
            if User.query.filter_by(email=session.get('email')).scalar():
                return redirect('success')
            else:
                return redirect('fail')

        # Don't allow user to register (email exist)    
        return redirect('used_email')

    return render_template(
        'register.html',
        form=form
    )

# 2.3 USER REGISTRATION UNSUCCESSFUL - NEW USER EMAIL EXIST
@app.route('/used_email')
def used_email():
    return render_template('user_exist.html', email=session.get('email'))

# 2.4 USER REGISTRATION SUCCESSFUL
@app.route('/success')
def success():
    return render_template('user_registered.html', name=session.get('name'), email=session.get('email'))    

# 3.0 DEFAULT PAGE FOR LOGGED-IN USER
@app.route('/books')
def books():

    # if user not logged in, redirect to login page
    if not session.get('SESSIONUSER'):
        return redirect(url_for('login'))
    
    # user logged in
    # render search form
    form = SearchForm()
    
    # list all books with pagination
    page = request.args.get('page', 1, type=int) # grab page from URL
    books = Book.query.order_by(Book.title).paginate(
        page = page,
        per_page = app.config['POST_PER_PAGE']
    )

    href_url = "\{\{ url_for('author', author=author, page=page) \}\}"

    return render_template('books.html', user=session.get('SESSIONUSER'), form=form, books=books, href_url=href_url)

# 3.1 GET BOOKS FROM AUTHOR
# if user click on author name from /books -> list all books from author:
@app.route('/author/<string:author>')
def author(author):

    # render search form
    form = SearchForm()

    # list all books published by same author (book_author)
    page = request.args.get('page', 1, type=int)

    # check if author exist
    author = Book.query.filter_by(author=author).first_or_404().author

    # fetch books by author
    books = Book.query.filter_by(author=author).order_by(Book.year.desc()).paginate(
        page,
        app.config['POST_PER_PAGE'],
        False
    )

    return render_template('author_books.html', 
                user=session.get('SESSIONUSER'), 
                form=form, 
                books=books, 
                author=author)

# 3.2 GET BOOK BY ISBN
# if user click on book title or book isbn number from /books -> render book info and user comments
@app.route('/isbn/<string:book_isbn>')
def book_isbn(book_isbn):
    
    # checks if author exists
    book = Book.query.filter_by(isbn=book_isbn).first_or_404()
    
    return render_template('book.html', book=book)

if __name__ == '__main__':
    app.run()