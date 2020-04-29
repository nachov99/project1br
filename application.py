import os

from flask import Flask, session, request, render_template
from flask_session.__init__ import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


from passlib.hash import sha256_crypt
app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html")

#REGISTER FORM
@app.route("/register", methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        confirm=request.form.get('confirm')
        secure_password=sha256_crypt.encrypt(str(password))

        usernamedata=db.execute("SELECT username FROM users WHERE  username=:username",{"username":username}).fetchone()
        if usernamedata==None:
            if password==confirm:
                db.execute("INSERT INTO users(username,password) VALUES(:username,:password)",
                {"username":username,"password":secure_password})
                db.commit()
                flash('You are registered and can now login','success')
                return redirect(url_for('login'))
            else:
                flash('password does not match','danger')
                return render_template('register.html')
        else:
            flash('user already existed, please login or contact admin','danger')
            return redirect(url_for('login'))

    return render_template('register.html')
