import os, json
from flask import Flask, session, request, render_template, jsonify, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
from logreq import login_required

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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
@login_required
def home():
    """ Show search box """

    return render_template("home.html")

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

    #Forget any user_id
    session.clear()

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

        checkuser = db.execute("SELECT * from users where username LIKE :username",
                        {'username': username}).fetchone()

        if not checkuser or not check_password_hash(checkuser.password, password):
            return render_template('error.html', message='Please check your login details and try again.')

        #Remember which user has logged in
        session['user_id'] = checkuser[0]
        session['user_name'] = checkuser[1]

        #Redirect user to home page
        return render_template('home.html')
    elif request.method=='GET':
        return render_template("login.html")

@app.route("/logout")
def logout():
    """ Log user out """

    # Forget any user ID
    session.clear()

    # Redirect user to login form
    return redirect("/")


#SEARCH BOX
@app.route("/search", methods=["GET"])
@login_required
def search():

    #Ensure if a book was provided
    if not request.args.get("book"):
        return render_template("error.html", message="You must provide a book.")

    # With this the user can type the first 3 leters of any string
    query = "%" + request.args.get("book") + "%"

    #This will let the user search for the author with no need to capitalize each word.
    query = query.title()

    rows = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn LIKE :query OR title LIKE :query OR author LIKE :query",
                        {"query": query})

    # Books not founded
    if rows.rowcount == 0:
        return render_template("error.html", message="we can't find books with that description.")

    # Search for the results
    books = rows.fetchall()

    return render_template("results.html", books=books)


#@app.route("/book/<isbn>", methods = ['GET','POST'])
@app.route("/book/<isbn>", methods=['GET','POST'])
@login_required
def book(isbn):
    if request.method == 'POST':

        #Save current session
        currentUser = session["user_id"]

        #Request for book database
        rating = request.form.get('rating')
        comment = request.form.get('comment')

        #Search for book id by isbn
        bookResult = db.execute('SELECT isbn FROM books WHERE isbn LIKE :isbn',
                                {"isbn": isbn}).fetchone()

        #Save book_id into a variable
        book_id = bookResult
        book_id = book_id[0]

        #Check if user already submitted a review for that book
        userSub = db.execute('SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id',
                            {'user_id': currentUser, 'book_id': book_id})

        #If review already exists
        if userSub.rowcount == 1:
            flash("You've already submitted a review for this book")
            return redirect("/book" + isbn)

        #Save review into
        rating = int(rating)

        db.execute('INSERT INTO reviews (user_id, book_id, comment, rating) VALUES (:user_id, :book_id, :comment, :rating)',
                    {'user_id': currentUser, 'book_id': book_id, 'comment': comment, 'rating': rating})

        db.commit()

        flash('Review submitted!')

        return redirect("/book/" + isbn)
    elif request.method == 'GET':
        row = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn = :isbn",
                        {"isbn": isbn})

        bookInfo = row.fetchall()

        #GOODREADS REVIEWS

        # Read API key from env variable
        #key = os.getenv("GOODREADS_KEY")
        key = 'PntQoVaB2YSKLpy9P0RGug'

        # Query the api with key and ISBN as parameters
        query = requests.get("https://www.goodreads.com/book/review_counts.json",
                params={"key": key, "isbns": isbn})

        # Convert the response to JSON
        response = query.json()

        # "Clean" the JSON before passing it to the bookInfo list
        response = response['books'][0]

        # Append it as the second element on the list. [1]
        bookInfo.append(response)

        #users review

         # Search book_id by ISBN
        row = db.execute("SELECT isbn FROM books WHERE isbn = :isbn",
                        {"isbn": isbn})

        # Save id into variable
        book = row.fetchone() # (id,)
        book = book[0]

        # Fetch book reviews
        results = db.execute("SELECT user_id, comment, rating FROM reviews WHERE book_id = :book",
                            {"book": book})

        reviews = results.fetchall()

        return render_template("book.html", bookInfo=bookInfo, reviews=reviews)

#API
@app.route("/api/book/<book_id>", methods = ["GET"])
def book_api(book_id):
    """Return details about a single book review."""
    # Make sure book review exists
    results = db.execute("SELECT * FROM reviews WHERE book_id = :book_id",
                        {"book_id": book_id})
    review = results.fetchall()
    if review is None:
        return jsonify({"error": "Invalid isbn"}), 422

    #Get all reviews from that book
    reviews = db.execute("SELECT user_id, book_id, comment, rating FROM reviews WHERE book_id = :book_id",
                        {"book_id": book_id})
    row = reviews.fetchall()
    return jsonify({
            "user": row.user_id,
            "isbn": row.book_id,
            "comment": row.comments,
            "rating": row.rating
        })


if __name__ == "__main__":
    app.run(debug=True)
