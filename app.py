from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'sarath@'

# Database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            age INTEGER NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Home
@app.route('/')
def home():
    return render_template('login.html')

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        age = request.form['age']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (email, age, password) VALUES (?, ?, ?)', (email, age, password))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'error')
        finally:
            conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['email'] = user[1]
            session['age'] = user[2]
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password!', 'error')
    return render_template('login.html')

# Profile
@app.route('/profile')
def profile():
    if 'user_id' in session:
        user = {
            'id': session['user_id'],
            'email': session['email'],
            'age': session['age']
        }
        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))

# Edit
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_email = request.form['email']
        new_age = request.form['age']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET email = ?, age = ? WHERE id = ?', (new_email, new_age, session['user_id']))
        conn.commit()
        conn.close()

        session['email'] = new_email
        session['age'] = new_age
        return redirect(url_for('profile'))

    return render_template('edit.html', user={'email': session['email'], 'age': session['age']})

# Delete
@app.route('/delete', methods=['POST'])
def delete():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (session['user_id'],))
    conn.commit()
    conn.close()

    session.clear()
    return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)