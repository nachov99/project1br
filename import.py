import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# database engine object from SQLAlchemy that manages connections to the database
engine = create_engine('postgres://pckgaxnrveaneq:b95fe71a9ca8dfb956cf64e39a0a791951436d4ee3235f563325d284fdfddb7e@ec2-52-86-73-86.compute-1.amazonaws.com:5432/dacuqeovgq7jhr')

# create a 'scoped session' that ensures different users' interactions with the
# database are kept separate
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open('books.csv')
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {'isbn': isbn, 'title': title, 'author': author, 'year': year})
        print(f"Added book {isbn} to database.")
    db.commit()

if __name__ == '__main__':
     main()
