from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import MySQLdb.cursors

auth = Flask(__name__)
auth.secret_key = 'your_secret_key'


auth.config['MYSQL_HOST'] = 'localhost'
auth.config['MYSQL_USER'] = 'root'
auth.config['MYSQL_PASSWORD'] = ''
auth.config['MYSQL_DB'] = 'waste_management_db'


mysql = MySQL(auth)
bcrypt = Bcrypt(auth)

@auth.route('/')
def index():
    return render_template('index.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', (name, email, hashed_password))
        mysql.connection.commit()
        cursor.close()
        
        flash('You have successfully signed up! Please log in.', 'success')
        return redirect(url_for('login'))

    return redirect('/')  

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['your_email']  
        password = request.form['your_pass']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', [email])
        user = cursor.fetchone()
        
        if user and bcrypt.check_password_hash(user['password'], password):
            session['loggedin'] = True
            session['id'] = user['id']
            session['name'] = user['name']
            flash('Welcome, ' + user['name'], 'success')
            return redirect(url_for('dashboard'))  
        else:
            flash('Login failed. Please check your credentials.', 'danger')
    
    return redirect('/') 

@auth.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return f"Hello, {session['name']}! Welcome to your dashboard."
    else:
        return redirect(url_for('login'))

@auth.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    auth.run(debug=True)
