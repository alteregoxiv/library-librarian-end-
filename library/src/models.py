from enum import unique
from . import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
import os

USER = os.environ["USER"]
PASS = os.environ["PASS"]

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + USER + ':' + PASS + '@arjuna.db.elephantsql.com/kixztwtw'

db = SQLAlchemy(app)


class books(db.Model):
    id = db.Column('book_id' , db.Integer , primary_key=True)
    title = db.Column(db.String(100) , nullable=False)
    author = db.Column(db.String(100) , nullable=False)
    isbn = db.Column(db.String(100) , nullable=False)
    publisher = db.Column(db.String(100) , nullable=False)

    def __init__(self , title , author , isbn , publisher):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.publisher = publisher


class members(db.Model):
    id = db.Column('member_id' , db.Integer , primary_key=True)
    name = db.Column(db.String(100) , nullable=False)
    email = db.Column(db.String(100) , nullable=False , unique=True)
    count = db.Column(db.Integer , nullable=False)
    total_transactions = db.Column(db.Integer , nullable=False)
    paid = db.Column(db.Float , nullable=False)
    debt = db.Column(db.Float , nullable=False)

    def __init__(self , name , email):
        self.name = name
        self.email = email
        self.count = 0
        self.total_transactions = 0
        self.paid = 0
        self.debt = 0


class librarian(db.Model):
    id = db.Column('librarian_id' , db.Integer , primary_key=True)
    name = db.Column(db.String(100) , nullable=False)
    email = db.Column(db.String(100) , nullable=False , unique=True)
    password = db.Column(db.String(300) , nullable=False)
    transactions = db.Column(db.Integer , nullable=False)
    current_issues = db.Column(db.Integer , nullable=False)

    def __init__(self , name , email , password):
        self.name = name
        self.email = email
        self.password = password
        self.transactions = 0
        self.current_issues = 0


class transactions(db.Model):
    id = db.Column('transaction_id' , db.Integer , primary_key=True)
    rent = db.Column(db.Float , nullable=False)
    book_id = db.Column(db.Integer , db.ForeignKey("books.book_id" , ondelete="CASCADE") , nullable=False)
    member_id = db.Column(db.Integer , db.ForeignKey("members.member_id" , ondelete="CASCADE") , nullable=False)
    librarian_id = db.Column(db.Integer , db.ForeignKey("librarian.librarian_id" , ondelete="CASCADE") , nullable=False)

    def __init__(self , rent , bid , mid , lid):
        self.rent = rent
        self.book_id = bid
        self.member_id = mid
        self.librarian_id = lid
