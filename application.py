import os, json
from flask import Flask, session, request, render_template, jsonify, flash, redirect, url_for, login
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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

        #Insert user data in database
        db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)",
                    {"username": username, "email": email, "password": password})
        db.commit()

        flash('Registration successful')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route("/login", methods=['GET','POST'])


def login():
    if request.method=='POST':

        login_manager = LoginManager()
        loginmanager.init_app(app)




        #Request for user data
        username=request.form.get('username')
        password=request.form.get('password')

        #Ensure username was submitted
        if not request.form.get('username'):
            return render_template('error.html', message='Please enter a username')

        #Ensure password was submitted
        elif not request.form.get('password'):
            return render_template('error.html', message='Please enter a password')

        #Search in the database for the username and Password
        #resultUNAME = db.execute('SELECT username, password FROM users WHERE username LIKE :username AND password LIKE :password',
        #                    {'username': username, 'password': password})
        #resultPSSW = db.execute('SELECT password FROM users WHERE password LIKE :password',
        #                    {'password': password})
        #if resultUNAME == username and resultPSSW == password:
        #    return render_template('error.html', message='Valid user data')
        #else:
        #    return render_template('error.html', message='User data incorrect')

        #Using Flask-login

    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)
