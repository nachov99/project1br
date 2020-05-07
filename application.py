import os, json
from flask import Flask, session, request, render_template, jsonify, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
#    raise RuntimeError("DATABASE_URL is not set")
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://pckgaxnrveaneq:b95fe71a9ca8dfb956cf64e39a0a791951436d4ee3235f563325d284fdfddb7e@ec2-52-86-73-86.compute-1.amazonaws.com:5432/dacuqeovgq7jhr'


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
#engine = create_engine(os.getenv("DATABASE_URL"),encoding="utf8")
engine = create_engine('postgres://pckgaxnrveaneq:b95fe71a9ca8dfb956cf64e39a0a791951436d4ee3235f563325d284fdfddb7e@ec2-52-86-73-86.compute-1.amazonaws.com:5432/dacuqeovgq7jhr')
db = scoped_session(sessionmaker(bind=engine))

#Setting up secret key.
app.secret_key = b'H\x1b\x89\x83|\xe3\x8b:a,\xd1I\xb5\xe6\xf2D'

@app.route("/")
def index():
    return render_template("index.html")

#REGISTER FORM
@app.route("/register", methods=['GET','POST'])
def register():
    if request.method=='POST':

        #Forget any user_id
        session.clear()

        #Request for user data
        username=request.form.get('username')
        email = request.form.get('email')
        password=request.form.get('password')

        #Ensure username was submitted
        if not request.form.get('username'):
            return render_template('error.html', message='Please enter a username')

        #Ensure password was submitted
        elif not request.form.get('password'):
            return render_template('error.html', message='Please enter a password')

        #If this returns a user, then the username already exists in database
        userverify = db.execute("SELECT * from users where username LIKE :username",
                        {'username': request.form.get('username')}).fetchone()
        if userverify:
            return render_template("error.html", message='Please enter a valid username')

        #Hash user password
        hashPssw = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)

        #Insert user data in database
        db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)",
                    {"username": username, "email": email, "password": hashPssw})
        db.commit()

        flash('Registration successful')
        return redirect(url_for('login'))
    else:
        return render_template("register.html")

#LOGIN FORM
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method=='POST':

        #Forget any user_id
        session.clear()

        #Request for user data
        username=request.form.get('username')
        password=request.form.get('password')

        #Ensure username was submitted
        if not request.form.get('username'):
            return render_template('error.html', message='Please enter a username')

        #Ensure password was submitted
        elif not request.form.get('password'):
            return render_template('error.html', message='Please enter a password')

        checkuser = db.execute("SELECT * from users where username LIKE :username",
                        {'username': request.form.get('username')}).first()

        if not checkuser or not check_password_hash(checkuser.password, password):
            return render_template('error.html', message='Please check your login details and try again.')

        #Remember which user has logged in
        session['user_id'] = checkuser[0]
        session['user_name'] = checkuser[1]

        #Redirect user to home page
        return render_template('home.html')
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """ Log user out """

    # Forget any user ID
    session.clear()

    # Redirect user to login form
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
