import os, json
from flask import Flask, session, request, render_template, jsonify, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flas_login import UserMixin

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"),encoding="utf8")
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
        #Request for user data
        username=request.form.get('username')
        email = request.form.get('email')
        password=request.form.get('password')

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
    return render_template('register.html')

#LOGIN FORM
@app.route("/login", methods=['GET','POST'])


def login():
    if request.method=='POST':

        #Request for user data
        username=request.form.get('username')
        password=request.form.get('password')

        #Ensure username was submitted
        if not request.form.get('username'):
            return render_template('error.html', message='Please enter a username')

        #Ensure password was submitted
        elif not request.form.get('password'):
            return render_template('error.html', message='Please enter a password')

        chekuser = db.execute("SELECT * from users where username LIKE :username",
                        {'username': request.form.get('username')}).first()

        if not user or not check_password_hash(user.password, password):
            return render_template('error.html', message='Please check your login details and try again.')

    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)
