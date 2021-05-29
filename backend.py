from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'eman'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = '4C6VCCbEB2'
app.config['MYSQL_PASSWORD'] = 'rFusYnkNpu'
app.config['MYSQL_DB'] = '4C6VCCbEB2'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['JSON_AS_ASCII'] = False


# Intialize MySQL
mysql = MySQL(app)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id']=account['id']
            session['username'] = username
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/login/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'Gender' in request.form and 'DOB' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        Gender = request.form['Gender']
        DOB = request.form['DOB']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
            return redirect(url_for('login'))
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s,%s,%s)', (username, password, email,Gender,DOB,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('login'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)   

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/login/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        cur = mysql.connection.cursor()
        query = f'SELECT img, Name, id FROM MOVIES'
        cur.execute(query)
        movies = cur.fetchall()
        return render_template('home.html', username=session['username'],movies=movies)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/login/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/Top_Revenue')
def m_revenue():
    cur = mysql.connection.cursor()
    query = f'SELECT img, id, Name, Revenue FROM MOVIES ORDER BY Revenue DESC LIMIT 10'
    cur.execute(query)
    revenue = cur.fetchall()
    return render_template('revenue.html', revenue=revenue) 
    
@app.route('/movie/<genre>')
def genre(genre):
    cur = mysql.connection.cursor()
    query = f'SELECT MOVIES.img, MOVIES.id, MOVIES.Name, genre.Genre FROM MOVIES, genre WHERE genre.id=MOVIES.id AND genre.Genre="{genre}";'
    cur.execute(query)
    genre = cur.fetchall()
    return render_template('genre.html', genre=genre) 

@app.route('/<movie>')
def movie(movie):
    cur = mysql.connection.cursor()
    query = f'SELECT img, id, Name, age_rate, Release_Date, Revenue, Duration, Rating, Description FROM MOVIES WHERE id={movie};'
    cur.execute(query)
    movies = cur.fetchall()
    query2= f'SELECT CAST.img, CAST.id, CAST.Name, castandmovie.Role FROM MOVIES, castandmovie, CAST WHERE castandmovie.m_id=MOVIES.id AND castandmovie.c_id=CAST.id AND MOVIES.id={movie};'
    cur.execute(query2)
    cast = cur.fetchall()
    query3= f'SELECT genre.Genre FROM MOVIES, genre WHERE genre.id=MOVIES.id AND MOVIES.id={movie};'
    cur.execute(query3)
    genre = cur.fetchall()
    query4= f'SELECT review.displayed_name, review.Rating, review.Review FROM review, MOVIES WHERE review.movie_id=MOVIES.id AND MOVIES.id={movie};'
    cur.execute(query4)
    review = cur.fetchall()
    return render_template('movie.html', movies=movies[0], cast=cast, genre=genre, review=review)        

@app.route('/cast/<cast>')
def cast(cast):
    cur = mysql.connection.cursor()
    query2= f'SELECT MOVIES.img, MOVIES.id, MOVIES.Name, castandmovie.Role FROM MOVIES, castandmovie, CAST WHERE castandmovie.m_id=MOVIES.id AND castandmovie.c_id=CAST.id AND CAST.id={cast};'
    cur.execute(query2)
    movies = cur.fetchall()
    print (movies)
    query = f'SELECT c.img, c.id, c.Name, c.Country, c.date_of_birth, c.Biography FROM CAST c WHERE c.id={cast}'
    cur.execute(query)
    cast = cur.fetchall()
    print(cast)
    return render_template('cast.html', cast=cast[0],movies=movies)  

@app.route('/<movie_id>/review', methods=['GET', 'POST'])
def review(movie_id):
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'displayed_name' in request.form and 'Rating' in request.form and 'Review' in request.form:
        # Create variables for easy access
        cursor = mysql.connection.cursor()
        displayed_name = request.form['displayed_name']
        Rating = request.form['Rating']
        review = request.form['Review']
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
        query=('INSERT INTO review (username,displayed_name,movie_id,review,Rating) VALUES (%s,%s,%s,%s,%s)')
        print(query)
        cursor.execute(query,(session['username'],displayed_name,movie_id,review,Rating))
        mysql.connection.commit()   
        return redirect(url_for('home'))
    return render_template('review.html')
    