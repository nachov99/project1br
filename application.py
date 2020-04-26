import os
import requests

from flask import Flask,render_template,flash,url_for,session, logging,request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'postgres://xheausojwaqqkz:1960ab72edccd1494a5c286a7d270b3c33ee82af85d9abb2e135bb91e7440202@ec2-34-197-212-240.compute-1.amazonaws.com:5432/dait7qu0pcaeop'

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
    return render_template("templates/index.html")
