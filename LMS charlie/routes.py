from flask import request, jsonify, render_template
from app import app, db
from models import Book, User
from datetime import datetime, timedelta

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/books', methods=['GET'])
def list_books():
    books = Book.query.all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'year': book.year,
        'is_available': book.is_available
    } for book in books])

@app.route('/borrow', methods=['POST'])
def borrow_book():
    data = request.json
    book = Book.query.get(data['book_id'])
    user = User.query.filter_by(username=data['username']).first()
    if book and user and book.is_available:
        book.is_available = False
        book.borrow_date = datetime.now()
        book.borrow_duration = data['duration']
        user.borrowed_books.append(book)
        db.session.commit()
        return jsonify({'message': 'Book borrowed successfully'})
    return jsonify({'message': 'Invalid request'}), 400

@app.route('/return', methods=['POST'])
def return_book():
    data = request.json
    book = Book.query.get(data['book_id'])
    user = User.query.filter_by(username=data['username']).first()
    if book and user and not book.is_available:
        book.is_available = True
        book.borrow_date = None
        book.borrow_duration = None
        user.borrowed_books.remove(book)
        db.session.commit()
        return jsonify({'message': 'Book returned successfully'})
    return jsonify({'message': 'Invalid request'}), 400

@app.route('/feedback', methods=['POST'])
def provide_feedback():
    data = request.json
    book = Book.query.get(data['book_id'])
    if book:
        return jsonify({'message': f'Feedback on "{book.title}": {data["feedback"]}'})
    return jsonify({'message': 'Invalid book ID'}), 400

@app.route('/request', methods=['POST'])
def request_book_to_add():
    data = request.json
    existing_book = Book.query.filter_by(title=data['title']).first()
    if existing_book:
        return jsonify({'message': 'Book already exists in the catalog'})
    new_book = Book(
        title=data['title'],
        author=data['author'],
        year=data['year'],
        is_available=False,
        requested_by=data['username']
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book requested to add to the catalog'})

@app.route('/admin/approve', methods=['POST'])
def admin_approve_book_request():
    data = request.json
    book = Book.query.filter_by(title=data['title'], is_available=False).first()
    if book:
        book.is_available = True
        book.requested_by = None
        db.session.commit()
        return jsonify({'message': 'Book request approved'})
    return jsonify({'message': 'Invalid book title'}), 400

@app.route('/admin/remove', methods=['POST'])
def admin_remove_requested_book():
    data = request.json
    book = Book.query.filter_by(title=data['title'], is_available=False).first()
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Requested book removed'})
    return jsonify({'message': 'Invalid book title'}), 400

@app.route('/admin/requested', methods=['GET'])
def view_requested_books_to_add():
    books = Book.query.filter(Book.is_available == False, Book.requested_by != None).all()
    return jsonify([{
        'title': book.title,
        'author': book.author,
        'year': book.year,
        'requested_by': book.requested_by
    } for book in books])

@app.route('/borrowed', methods=['GET'])
def view_borrowed_books():
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify([{
            'title': book.title,
            'author': book.author,
            'year': book.year
        } for book in user.borrowed_books])
    return jsonify({'message': 'Invalid username'}), 400

@app.route('/borrowed/fines', methods=['GET'])
def view_borrowed_books_with_fines():
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        borrowed_books = []
        for book in user.borrowed_books:
            return_date = book.borrow_date + timedelta(days=book.borrow_duration)
            fine = max(0, (datetime.now() - return_date).days * 5)
            borrowed_books.append({
                'title': book.title,
                'return_by': return_date.strftime('%Y-%m-%d'),
                'fine': fine
            })
        return jsonify(borrowed_books)
    return jsonify({'message': 'Invalid username'}), 400

@app.route('/admin/deadlines', methods=['GET'])
def admin_view_customer_deadlines():
    users = User.query.all()
    deadlines = []
    for user in users:
        for book in user.borrowed_books:
            return_date = book.borrow_date + timedelta(days=book.borrow_duration)
            fine = max(0, (datetime.now() - return_date).days * 5)
            deadlines.append({
                'username': user.username,
                'title': book.title,
                'return_by': return_date.strftime('%Y-%m-%d'),
                'fine': fine
            })
    return jsonify(deadlines)

@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registration successful'})

@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        return jsonify({'message': 'Login successful'})
    return jsonify({'message': 'Invalid username or password'}), 400