from app import db

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    borrow_date = db.Column(db.DateTime, nullable=True)
    borrow_duration = db.Column(db.Integer, nullable=True)
    requested_by = db.Column(db.String(100), nullable=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    borrowed_books = db.relationship('Book', backref='borrower', lazy=True)