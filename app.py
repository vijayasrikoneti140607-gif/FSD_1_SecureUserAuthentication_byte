import os, sqlite3
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, session, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'local-dev-only-change-me')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('COOKIE_SECURE', 'false').lower() == 'true'
csrf = CSRFProtect(app)
DB = os.getenv('DATABASE_PATH', os.path.join(os.path.dirname(__file__), 'users.db'))

def connect():
    db = sqlite3.connect(DB, timeout=20)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL)')

def protected(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify(error='Authentication required'), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return inner

@app.get('/')
def home(): return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET': return render_template('register.html')
    username = request.form.get('username','').strip()
    email = request.form.get('email','').strip().lower()
    password = request.form.get('password','')
    if not username or '@' not in email or len(password) < 8:
        return render_template('register.html', error='Enter a username, valid email and password of at least 8 characters.'), 400
    try:
        with connect() as db:
            db.execute('INSERT INTO users(username,email,password) VALUES(?,?,?)', (username,email,generate_password_hash(password)))
    except sqlite3.IntegrityError:
        return render_template('register.html', error='Username or email already registered.'), 409
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET': return render_template('login.html')
    email = request.form.get('email','').strip().lower()
    password = request.form.get('password','')
    if not email or not password: return render_template('login.html', error='Email and password required.'), 400
    with connect() as db:
        user = db.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
    if not user or not check_password_hash(user['password'],password):
        return render_template('login.html', error='Invalid email or password.'), 401
    session.clear()
    session['user_id'], session['username'] = user['id'], user['username']
    return redirect(url_for('dashboard'))

@app.get('/dashboard')
@protected
def dashboard(): return render_template('dashboard.html', username=session['username'])

@app.get('/api/profile')
@protected
def profile(): return jsonify(message='Authenticated successfully',username=session['username'])

@app.post('/logout')
@protected
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.get('/health')
def health(): return jsonify(status='ok')

init_db()
if __name__ == '__main__': app.run(host='0.0.0.0', port=int(os.getenv('PORT',5000)))
