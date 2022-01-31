from flask import request , render_template , session , redirect
import requests , json
from flask.helpers import flash
from werkzeug.security import generate_password_hash , check_password_hash
from .models import db , librarian , transactions , members , books 
from . import app


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


@app.route('/')
def index():
    a = members.query.all()
    b = books.query.all()

    l = []
    for i in a:
        l += [(i.paid , i.name)]
    l = sorted(l , key=lambda i:i[0])
    
    c = 0
    d = {}  
    for i in b:
        c += 1
        if i.title not in d:
            d[i.title] = 1
        else:
            d[i.title] += 1
    q = sorted(d.items() , key=lambda i:i[1])
    if c<15:
        c = 15 - c

    maxall = []
    if len(l)>0:
        maxall += [l[-1]]
    else:
        maxall += [[]]

    if len(q)>0:
        maxall += [q[-1]]
    else:
        maxall += [[]]
    maxall += [c]

    return render_template("index.html" , maxall=maxall)

@app.route('/new_books' , methods=['GET' , 'POST'])
def new_books():
    if "email" not in session:
        flash("Please login first" , "warning")
        return redirect("/login")
    if request.method=="GET":
        title = request.args.get("title")
        httpresponse = requests.get("https://frappe.io/api/method/frappe-library?title=" + title)
        textdata = httpresponse.text
        jsondata = json.loads(textdata)

        return render_template("new_books.html" , data=jsondata)
    else:
        title = request.form.get("title")
        authors = request.form.get("authors")
        isbn = request.form.get("isbn")
        publisher = request.form.get("publisher")

        a = books(title , authors , isbn , publisher)
        db.session.add(a)
        db.session.commit()

        msg = title + " was successfully added to the library"
        flash(msg , "success")
        return redirect(request.referrer)

@app.route('/removebook' , methods=['POST'])
def removebook():
    a = books.query.get(request.form.get("book_id"))
    s = a.title
    db.session.delete(a)
    db.session.commit()
    flash("1 piece of " + s + " removed from library" , "success")
    return redirect("/library")



@app.route('/membersinfo' , methods=['GET' , 'POST'])
def membersinfo():
    if request.method=="GET":
        if request.args:
            a = members.query.get(request.args.get("memberid"))
            if a is None:
                return render_template("memberinfo.html" , data=[])
            else:
                return render_template("memberinfo.html" , data=[a])
        else:
            return render_template("memberinfo.html" , data=members.query.all())
    else:
        a = members.query.get(request.form.get("member_id"))
        db.session.delete(a)
        db.session.commit()
            
        return render_template("memberinfo.html" , data=members.query.all())


@app.route('/createmember' , methods=["GET" , "POST"])
def createmember():
    if request.method=="GET":
        return render_template("createmember.html")
    else:
        name = request.form.get("membername")
        email = request.form.get("memberemail")

        a = members(name , email)
        db.session.add(a)
        db.session.commit()

        flash("User " + email + " created" , "success")
        return render_template("createmember.html")


@app.route('/librarianinfo')
def librarianinfo():
    a = librarian.query.get(session['id'])
    return render_template("librarianinfo.html" , data=a)



@app.route('/alltransactions' , methods=['GET' , 'POST'])
def alltransactions():
    if request.method=="GET":
        if request.args:
            a = transactions.query.filter(transactions.id==request.args.get("transactionid")).first()
            if a is None:
                return render_template("transaction.html" , data=[])
            else:
                return render_template("transaction.html" , data=[a])
        else:
            a = transactions.query.all()
            return render_template("transaction.html" , data=a)
    else:
        transactionid = request.form.get("transaction_id")
        a = transactions.query.filter(transactions.id==transactionid).first()
        b = members.query.filter(members.id==a.member_id).first()
        c = librarian.query.filter(librarian.id==a.librarian_id).first()
        b.paid += a.rent
        b.debt -= a.rent
        b.count -= 1
        c.current_issues -= 1
        db.session.delete(a)
        db.session.commit()
        return render_template("transaction.html" , data=transactions.query.all())





@app.route("/library")
def library():
    a = books.query.all()
    b = transactions.query.all()
    issued = []
    for i in b:
        issued += [i.book_id]
    
    if len(a)==0:
        return render_template("library.html" , data=[])
    else:
        return render_template("library.html" , data=a , issued=issued)

@app.route("/filterlibrary")
def filterlibrary():
    if len(request.args)>0:
        title = request.args.get('title')
        author = request.args.get("author") 
        isbn = request.args.get("isbn")
        publisher = request.args.get("publisher")

        a = transactions.query.all()
        issued = []
        for i in a:
            issued += [i.book_id]

        l = []
        if not title=="":
            title = "%" + title + "%"
            l += [books.title.like(title)]

        if not author=="":
            author = "%" + author + "%"
            l += [books.author.like(author)]

        if not isbn=="":
            isbn = "%" + isbn + "%"
            l += [books.isbn.like(isbn)]

        if not publisher=="":
            publisher = "%" + publisher + "%"
            l += [books.publisher.like(publisher)]
        
        if len(l)==0:
            return render_template("filterlibrary.html" , data=[])
        elif len(l)==1:
            data = books.query.filter(l[0]).all()
        elif len(l)==2:
            data = books.query.filter(l[0] , l[1]).all()
        elif len(l)==3:
            data = books.query.filter(l[0] , l[1] , l[2]).all()
        elif len(l)==4:
            data = books.query.filter(l[0] , l[1] , l[2] , l[3]).all()
    
        return render_template("filterlibrary.html" , data=data , issued=issued)
    else:
        return render_template("filterlibrary.html" , data=[])

@app.route("/filtersearch")
def filtersearch():
    if len(request.args)>0:
        title = request.args.get('title')
        author = request.args.get("author") 
        isbn = request.args.get("isbn")
        publisher = request.args.get("publisher")
        
        s = "https://frappe.io/api/method/frappe-library?"
        if title:
            s += "title="+title+"&"
        if author:
            s += "authors="+author+"&"
        if isbn:
            s += "isbn="+isbn+"&"
        if publisher:
            s += "publisher="+publisher+"&"

        httpresponse = requests.get(s)
        textdata = httpresponse.text
        jsondata = json.loads(textdata)

        data = []
        for i in jsondata["message"]:
            if (title.lower() in i["title"].lower()) and (author.lower() in i["authors"].lower()) and (isbn.lower() in
                    i["isbn"].lower()) and (publisher.lower() in i["publisher"].lower()):
                data.append(i)
        
        
        return render_template("filtersearch.html" , data=data)
    else:
        return render_template("filtersearch.html" , data=[])




@app.route("/issue" , methods=['GET' , 'POST'])
def issue():
    if request.method=='GET':
        return render_template("issue.html" , bookid=request.args.get("bookid"))
    else:
        bookid = request.form.get("bookid")
        librarianid = request.form.get("librarianid")
        memberid = request.form.get("memberid")
        rent = float(request.form.get("rent"))

        a = members.query.filter(members.id==memberid).first()
        b = librarian.query.filter(librarian.id==librarianid).first()

        if a is None:
            flash("Invalid Member ID" , "danger")
            return redirect("/issue")
        else:
            if a.debt+rent>500:
                flash("Member should return books first" , "danger")
                return redirect("/library")

            a.total_transactions += 1
            a.count += 1
            a.debt += rent
            b.transactions += 1
            b.current_issues += 1
            
            c = transactions(rent , bookid , memberid , librarianid)
            db.session.add(c)
            db.session.commit()
            
            return redirect("/library")






@app.route('/login' , methods=['GET' , 'POST'])
def login():
    if request.method=="GET":
        return render_template("login.html")
    else:
        email = request.form.get("loginemail")
        pwd = request.form.get("loginpwd")

        a = librarian.query.filter(librarian.email==email).first()

        if a is None:           
            flash("Invalid Credentials" , "danger")
            return redirect("/login")
        elif check_password_hash(a.password , pwd):
            session['email'] = email
            session['name'] = a.name
            session['id'] = a.id
            msg = "Successfully Signed in as " + email
            flash(msg , "success")
            return redirect("/")
        else:
            flash("Invalid Credentials" , "danger")
            return redirect("/login")

@app.route('/logout')
def logout():
    session.pop('email' , None)
    session.pop('name' , None)
    session.pop('id' , None)
    flash("Successfully logged out" , "success")
    return redirect("/")

@app.route('/signin' , methods=['GET' , 'POST'])
def signin():
    if request.method=="GET":
        return render_template("signin.html")
    else:
        username = request.form.get("username")
        email = request.form.get("email")
        pwd = generate_password_hash(request.form.get("signinpwd") , "sha256")

        q = librarian.query.filter(librarian.email==email).first()

        if q is None:
            a = librarian(username , email , pwd)
            db.session.add(a)
            db.session.commit()

            a = librarian.query.filter(librarian.email==email).first()
            
            session['email'] = email
            session['name'] = username
            session['id'] = a.id

    
            msg = "Successfully Signed in as " + email
            flash(msg , "success")
            return redirect("/")
        else:
            flash("Email already used" , "danger")
            return redirect("/signin")

@app.route('/signout')
def signout():
    a = librarian.query.get(session['id'])
    name = session['name']

    session.pop('email' , None)
    session.pop('name' , None)
    session.pop('id' , None)

    db.session.delete(a)
    db.session.commit()

    flash(name + " is no longer a librarian" , "success")
    return redirect("/")
