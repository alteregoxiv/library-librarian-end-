from flask import Flask
app = Flask(__name__)
app.secret_key = "asdgbwdwqq23235343ytgwfsddasdfdqwqed#@w1ferg5@3324#3w342egfvdfdfdsff"

from .models import db , books , members , librarian , transactions
