from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "students.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Association table for courses
enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    courses = db.relationship('Course', secondary=enrollments, backref='students')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250))

# Initialize database
with app.app_context():
    db.create_all()
    default_courses = ['BIT', 'BCS', 'BBA', 'BSCIT']
    for cname in default_courses:
        if not Course.query.filter_by(course_name=cname).first():
            db.session.add(Course(course_name=cname, description=f"{cname} program"))
    db.session.commit()

# Routes
@app.route('/')
def home():
    return render_template('home.html')

# Register/Login/Logout
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']
        password = generate_password_hash(raw_password, method='pbkdf2:sha256')

        if User.query.filter_by(username=username).first():
            flash('Username exists!', 'danger')
            return redirect(url_for('register'))

        db.session.add(User(username=username, password=password))
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out!', 'success')
    return redirect(url_for('home'))

# Dashboard & Students
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Login first!', 'danger')
        return redirect(url_for('login'))

    search_query = request.args.get('search')

    if search_query:
        students = Student.query.filter(
            Student.name.contains(search_query)
        ).all()
    else:
        students = Student.query.all()

    return render_template('dashboard.html', students=students)



@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'user' not in session:
        flash('Login first!', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        s = Student(
            name=request.form['name'],
            age=request.form['age'],
            grade=request.form['grade'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address']
        )
        db.session.add(s)
        db.session.commit()
        flash('Student added!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_student.html')

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if 'user' not in session:
        flash('Login first!', 'danger')
        return redirect(url_for('login'))

    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        student.name = request.form['name']
        student.age = request.form['age']
        student.grade = request.form['grade']
        student.email = request.form['email']
        student.phone = request.form['phone']
        student.address = request.form['address']

        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_student.html', student=student)


@app.route('/view_student/<int:id>')
def view_student(id):
    if 'user' not in session:
        flash('Login first!', 'danger')
        return redirect(url_for('login'))

    student = Student.query.get_or_404(id)
    return render_template('view_student.html', student=student)


# Delete a student
@app.route('/delete_student/<int:id>')
def delete_student(id):
    if 'user' not in session:
        flash('Login first!', 'danger')
        return redirect(url_for('login'))
    
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/courses')
def courses():
    if 'user' not in session:
        flash('Login first!', 'danger')
        return redirect(url_for('login'))
    return render_template('courses.html', courses=Course.query.all())

# Run app
if __name__ == '__main__':
    app.run(debug=True, port=5002)
