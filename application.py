import os, json
from flask import Flask, session, request, render_template, jsonify, flash, redirect, url_for
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

@app.route("/")
def index():
    return render_template("index.html")

#REGISTER FORM
@app.route("/register", methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form.get('username')
        email = request.form.get('email')
        password=request.form.get('password')
        db.execute("INSERT INTO user (username, email, password) VALUES ( :username, :email, :password)",
                    {"username": username, "email": email,"password": password})
        db.commit()
        #example = db.execute("SELECT * FROM user").fetchall()
        #print(example)
        flash('Registration successful')
        return redirect(url_for('index'))
    return render_template('register.html')


if __name__ == "__main__":
    app.run(debug=True)
