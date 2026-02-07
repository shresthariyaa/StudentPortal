from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model (for login)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(50), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

# Dashboard - list students
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    students = Student.query.all()
    return render_template('dashboard.html', students=students)

# Add student
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'user' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        new_student = Student(name=name, age=age, grade=grade)
        db.session.add(new_student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_student.html')

# Edit student
@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if 'user' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.name = request.form['name']
        student.age = request.form['age']
        student.grade = request.form['grade']
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_student.html', student=student)

# Delete student
@app.route('/delete_student/<int:id>')
def delete_student(id):
    if 'user' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
