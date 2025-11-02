from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key_123"

# -------------------- DATABASE SETUP --------------------
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    # Default admin (only once)
    cursor.execute("INSERT OR IGNORE INTO admin (username, password) VALUES (?, ?)",
                   ("krushna", generate_password_hash("7777")))
    conn.commit()
    conn.close()

init_db()

# -------------------- LOGIN ROUTES --------------------
@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        admin = conn.execute("SELECT * FROM admin WHERE username=?", (username,)).fetchone()
        conn.close()

        if admin and check_password_hash(admin['password'], password):
            session['user'] = username
            flash("Login successful!", "success")
            return redirect('/dashboard')
        else:
            flash("Invalid username or password", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!", "info")
    return redirect('/login')

# -------------------- MAIN APP ROUTES --------------------

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) AS total FROM students").fetchone()['total']
    conn.close()
    return render_template('dashboard.html', total_students=count)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO students (name, email, course) VALUES (?, ?, ?)", (name, email, course))
            conn.commit()
            flash("Student added successfully!", "success")
        except sqlite3.IntegrityError:
            flash("Email already exists!", "warning")
        conn.close()
        return redirect('/students')

    return render_template('register.html')

@app.route('/students')
def students():
    if 'user' not in session:
        return redirect('/login')
    
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    if search_query:
        students = conn.execute("SELECT * FROM students WHERE name LIKE ? OR course LIKE ? OR email LIKE ?", 
                                (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%')).fetchall()
    else:
        students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template('students.html', students=students, search_query=search_query)

@app.route('/delete/<int:id>')
def delete_student(id):
    if 'user' not in session:
        return redirect('/login')
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Student deleted successfully!", "info")
    return redirect('/students')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if 'user' not in session:
        return redirect('/login')

    conn = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']
        conn.execute("UPDATE students SET name=?, email=?, course=? WHERE id=?", (name, email, course, id))
        conn.commit()
        conn.close()
        flash("Student updated successfully!", "success")
        return redirect('/students')

    conn.close()
    return render_template('edit.html', student=student)

# -------------------- RUN APP --------------------
if __name__ == '__main__':
    app.run(debug=True)
