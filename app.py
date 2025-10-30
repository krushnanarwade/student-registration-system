from flask import Flask, render_template, request, redirect, session
import sqlite3

import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()


app = Flask(__name__)
app.secret_key = "secret_key_123"   # REQUIRED for login session

# Create table if not exists
conn = sqlite3.connect('database.db', check_same_thread=False)
conn.execute('''CREATE TABLE IF NOT EXISTS students
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT, email TEXT, course TEXT)''')
conn.close()

# -------------------- LOGIN ROUTES --------------------

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Your Admin Login
        if username == "krushna" and password == "7777":
            session['user'] = username
            return redirect('/register')
        else:
            return render_template('login.html', error="Invalid Username or Password")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# -------------------- MAIN APP ROUTES --------------------

@app.route('/register')
def index():
    if 'user' not in session:
        return redirect('/login')
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    if 'user' not in session:
        return redirect('/login')

    name = request.form['name']
    email = request.form['email']
    course = request.form['course']

    conn = sqlite3.connect('database.db')
    conn.execute("INSERT INTO students (name, email, course) VALUES (?,?,?)", (name, email, course))
    conn.commit()
    conn.close()

    return redirect('/students')

@app.route('/students')
def students():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    data = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template('students.html', students=data)

if __name__ == '__main__':
    app.run(debug=True)
