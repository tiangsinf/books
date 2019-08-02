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
    return dict(app=app, db=db, User=User, Book=Book, Review=Review)

# 1.0 HOME ROUTE
# user not logged in
from forms import LoginForm, RegistrationForm, SearchForm, ReviewForm
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
            session['SESSIONUSER'] = user.id
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
@app.route('/books', methods=['GET', 'POST'])
def books():

    # if user not logged in, redirect to login page
    if not session.get('SESSIONUSER'):
        return redirect(url_for('login'))
    
    # user logged in
    # render search form
    form = SearchForm()
    user = User.query.get(session.get('SESSIONUSER'))
    # list all books with pagination
    page = request.args.get('page', 1, type=int) # grab page from URL

    books = Book.query.order_by(Book.title).paginate(
        page = page,
        per_page = app.config['ITEMS_PER_PAGE']
    )

    session.pop('q_title', None)
    session.pop('q_author', None)
    session.pop('q_isbn', None)
    session.pop('q_year', None)

    if request.method == 'POST':
        session['q_title'] = form.title.data
        session['q_author'] = form.author.data
        session['q_isbn'] = form.isbn.data
        session['q_year'] = form.year.data
        
        return redirect(url_for('results'))

    return render_template('books.html', user=user, form=form, books=books)

from sqlalchemy import func
@app.route('/results')
def results():
    form = SearchForm()
    user = User.query.get(session.get('SESSIONUSER'))
    page = request.args.get('page', 1, type=int)
    books = Book.query \
        .filter(func.lower(Book.title).contains(func.lower(f"{session.get('q_title')}"))) \
        .filter(Book.author.contains(f"{session.get('q_author')}")) \
        .filter(Book.isbn.contains(f"{session.get('q_isbn')}")) \
        .filter(Book.year == session.get('q_year')) \
        .order_by(Book.title) \
        .paginate(
            page = page,
            per_page = app.config['ITEMS_PER_PAGE']
        )        
    return render_template('search.html', user=user, form=form, books=books)

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
        page = page,
        per_page = app.config['ITEMS_PER_PAGE']
    )

    return render_template('author_books.html', 
                user=session.get('SESSIONUSER'), 
                form=form, 
                books=books, 
                author=author)

# 3.2 GET BOOK BY ISBN
# if user click on book title or book isbn number from /books -> render book info and user comments

def format_datetime(value, format="%d %b %Y %I:%M %p"):
    """Format a date time to (Default): d Mon YYYY HH:MM P"""
    if value is None:
        return ''
    return value.strftime(format)

app.jinja_env.filters['formatdatetime'] = format_datetime

@app.route('/isbn/<string:book_isbn>')
def book_isbn(book_isbn):
    
    page = request.args.get('page', 1, type=int)
    # checks if author exists
    book = Book.query.filter_by(isbn=book_isbn).first_or_404()
    reviews = book.comments.order_by(Review.review_date.desc())
    return render_template(
        'book.html', 
        book=book, 
        reviews=reviews.all(),
        reviews_pages=reviews.paginate(page=page, per_page=5)
        )

@app.route('/user_review/<int:book_id>', methods=['GET', 'POST'])
def user_review(book_id):
    form = ReviewForm()
    session['book'] = Book.query.get(book_id)

    if request.method == 'POST':
        session['review'] = form.review.data
        session['rating'] = form.rating.data
        
        review = Review(
            session.get('review'), 
            session.get('rating'),
        )

        user = User.query.get(session.get('SESSIONUSER'))
        review.user = user
        review.book = session.get('book')

        db.session.add(review)
        db.session.commit()

        return redirect(url_for('book_isbn', book_isbn=session.get('book').isbn))

    return render_template('user_review.html', form=form, book=session.get('book'))



if __name__ == '__main__':
    app.run()

