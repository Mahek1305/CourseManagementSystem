import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'Mahek123'

# DB CONFIG
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mahek@2005'
app.config['MYSQL_DB'] = 'CourseMagementSystem'

mysql = MySQL(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# ================= USER =================
class User(UserMixin):
    def __init__(self, user_id, username, email, password, role):
        self.id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.role = role

    def is_student(self):
        return self.role == 'Student'


@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Users WHERE user_id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return User(user['user_id'], user['username'], user['email'], user['password'], user['role'])
    return None


# ================= ROUTES =================
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            login_user(User(user['user_id'], user['username'], user['email'], user['password'], user['role']))
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid user")   # ✅ FLASH MESSAGE
            return redirect(url_for('login'))  # ✅ REDIRECT

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO Users(username,email,password,role) VALUES(%s,%s,%s,%s)",
                       (username, email, password, 'Student'))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/dashboard')
@login_required
def dashboard():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("""
        SELECT c.course_id, c.course_name, c.description
        FROM Courses c
        JOIN Enrollments e ON c.course_id = e.course_id
        WHERE e.student_id = %s
    """, (current_user.id,))

    courses = cursor.fetchall()
    cursor.close()

    return render_template('dashboard.html', username=current_user.username, courses=courses)


@app.route('/courses')
@login_required
def courses():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Courses WHERE status='Active'")
    courses = cursor.fetchall()
    cursor.close()

    return render_template('courses.html', courses=courses)


@app.route('/enroll/<int:id>')
@login_required
def enroll(id):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO Enrollments(student_id, course_id) VALUES(%s,%s)",
                   (current_user.id, id))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('dashboard'))


@app.route('/course/<int:id>')
@login_required
def course_details(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Courses WHERE course_id=%s", (id,))
    course = cursor.fetchone()
    cursor.close()

    return render_template('course_details.html', course=course)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# SAMPLE DATA
@app.route('/add_courses')
def add_courses():
    cursor = mysql.connection.cursor()
    data = [
        ('PY101', 'Python', 'Learn Python', 3, 1, 'CS', 'Active'),
        ('WD101', 'Web Dev', 'HTML CSS JS', 3, 1, 'CS', 'Active'),
        ('ML101', 'ML', 'Intro ML', 3, 1, 'AI', 'Active')
    ]

    for d in data:
        cursor.execute("""
        INSERT INTO Courses(course_code,course_name,description,credits,instructor_id,department,status)
        VALUES(%s,%s,%s,%s,%s,%s,%s)
        """, d)

    mysql.connection.commit()
    return "Courses Added"


if __name__ == '__main__':
    app.run(debug=True)