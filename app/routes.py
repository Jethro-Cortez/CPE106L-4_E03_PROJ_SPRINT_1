from flask import Blueprint, render_template, redirect, url_for, flash, request
from . import db
from .models import User, Book, Transaction, Feedback
from flask_login import login_user, logout_user, login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password_hash == password:
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            else:
                return redirect(url_for('main.user_dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        new_user = User(username=username, password_hash=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/user_dashboard')
@login_required
def user_dashboard():
    books = Book.query.all()
    return render_template('user_dashboard.html', books=books)

@main.route('/admin_dashboard')
@login_required
def admin_dashboard():
    books = Book.query.all()
    return render_template('admin_dashboard.html', books=books) 

@main.route('/request_book', methods=['POST'])
@login_required
def request_book():
    title = request.form.get('title')
    author = request.form.get('author')
    genre = request.form.get('genre')
    
    flash('Book request submitted successfully!')
    return redirect(url_for('main.user_dashboard'))

@main.route('/adminreg/sinigangmix', methods=['GET', 'POST'])
def admin_register(secret_key):
    if secret_key != 'sinigangmix':
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = 'admin'
        new_user = User(username=username, password_hash=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Admin registration successful! Please log in.')
        return redirect(url_for('main.login'))
    return render_template('adminreg.html')

@main.route('/book/<int:book_id>', methods=['GET'])
@login_required
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    feedbacks = Feedback.query.filter_by(book_id=book_id).all()
    return render_template('book_details.html', book=book, feedbacks=feedbacks)

@main.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.availability:
        book.availability = False
        new_transaction = Transaction(user_id=current_user.id, book_id=book.id)
        db.session.add(new_transaction)
        db.session.commit()
        flash('Book borrowed successfully!')
    else:
        flash('Book is not available.')
    return redirect(url_for('main.user_dashboard'))