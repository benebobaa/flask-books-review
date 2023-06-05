from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'any secret string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///glori.db'





db = SQLAlchemy(app)




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password
        
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    img = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    reviews = db.relationship('Review', backref='book', cascade='all, delete-orphan', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    rate = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    
with app.app_context():
    db.create_all()

@app.route('/books/upload', methods=['POST'])
def upload_books():
    title = request.form['title']
    author = request.form['author']
    pic = request.files['image']
    if not pic:
        return jsonify({'message': 'No image uploaded'}), 400
    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    
    
    img = Book(title = title, author = author, image_url= 'test', img=pic.read(), name=filename, mimetype=mimetype)
    
    db.session.add(img)
    db.session.commit()

    return jsonify({'message': 'add book success'}), 201
    

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    confirm_password = request.json.get('confirm_password')

    if not username or not password or not confirm_password:
        return jsonify({'message': 'Please provide username, password, and confirm_password'}), 400

    if password != confirm_password:
        return jsonify({'message': 'Passwords do not match'}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/cms/users', methods=['GET'])
def all_user():
    users = User.query.all()
    result = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'password': user.password
        }
        result.append(user_data)
    return jsonify(result), 200


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'message': 'Please provide username and password'}), 400

    user = User.query.filter_by(username=username).first()

    if not user or user.password != password:
        return jsonify({'message': 'Invalid username or password'}), 401

    return jsonify({'message': 'Login successful'}), 200

@app.route('/books/all', methods=['GET'])
def get_books():
    books = Book.query.all()
    result = []
    for book in books:
        book_data = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'image_url': request.host_url + 'books/image/' + str(book.id),
            # 'img': book.img,
            # 'filename': book.name,
            # 'mimetype': book.mimetype,
            'reviews': [{'user': review.user,'review': review.content, 'rate': review.rate} for review in book.reviews]
        }
        result.append(book_data)
    return jsonify(result), 200

@app.route('/cms/allbooks', methods=['GET'])
def get_books():
    books = Book.query.all()
    result = []
    for book in books:
        book_data = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'image_url': request.host_url + 'books/image/' + str(book.id),
            # 'img': book.img,
            # 'filename': book.name,
            # 'mimetype': book.mimetype,
            'reviews': [{'user': review.user,'review': review.content, 'rate': review.rate} for review in book.reviews]
        }
        result.append(book_data)
    return jsonify(result), 200

@app.route('/books/image/<int:img_id>', methods=['GET'])
def get_image(img_id):
    img = Book.query.filter_by(id=img_id).first()
    if not img:
        return jsonify({'message': 'Image not found'}), 404
    
    return Response( img.img, mimetype=img.mimetype)

@app.route('/books/add', methods=['POST'])
def create_book():
    data = request.get_json()
    book = Book(title=data['title'], author=data['author'] )
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': 'Book created successfully!'}), 201

@app.route('/books/<int:book_id>/review', methods=['POST'])
def create_review(book_id):
    data = request.get_json()
    if(data['user'] == '' or data['content'] == '' or data['rate'] == ''):
        return jsonify({'message': 'Please provide user, content, and rate'}), 400
    book = Book.query.get(book_id)
    if book is None:
        return jsonify({'message': 'Book not found.'}), 404
    review = Review(content=data['content'], user= data['user'], rate= data['rate'], book=book)
    db.session.add(review)
    db.session.commit()
    return jsonify({'message': 'Review created successfully!'})
    

# @app.route('/books/add', methods=['POST'])
# def create_book():
#     title = request.json.get('title')
#     description = request.json.get('description')

#     if not title or not description:
#         return jsonify({'message': 'Please provide title and description'}), 400

#     new_book = Book(title=title, description=description)
#     db.session.add(new_book)
#     db.session.commit()

#     return jsonify({'message': 'Book created successfully'}), 201


@app.route('/')
def index():
  return 'hello, this api created by beneboba :)'




if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000, debug=True)
