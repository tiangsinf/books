from run import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False, index=True)
    email = db.Column(db.String(128), nullable=False, index=True)
    password = db.Column(db.String(256), nullable=False)
    comments = db.relationship('Review', backref='user', lazy='dynamic')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return f'<email: {self.email}>'

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(64), index=True)
    title = db.Column(db.String(256), index=True)
    author = db.Column(db.String(256))
    year = db.Column(db.String(128))
    comments = db.relationship('Review', backref='book', lazy='dynamic')

    def __init__(self):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year

    def __repr__(self):
        return f'<title: {self.title}>'

import datetime
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.Text)
    rating = db.Column(db.Integer)
    review_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, review, rating):
        self.review = review
        self.rating = rating

    def __repr__(self):
        return f'<{self.review}>'