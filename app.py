from cs50 import SQL
import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///hotel.db")

db.execute("CREATE TABLE IF NOT EXISTS hotels (hotel_id INTEGER, username TEXT NOT NULL, hash TEXT NOT NULL, hotelname TEXT NOT NULL, tworoom NUMERIC NOT NULL, threeroom NUMERIC NOT NULL, apartments NUMERIC NOT NULL, PRIMARY KEY (hotel_id))")
db.execute("CREATE TABLE IF NOT EXISTS reservations (order_id INTEGER, hotel_id NUMERIC NOT NULL, resname TEXT NOT NULL, roomtype TEXT NOT NULL, fromdate TEXT NOT NULL, todate TEXT NOT NULL, PRIMARY KEY (order_id), FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id))")



number = 0

def checkdate(string):
    date_str = string
    try:
        date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return False
    datenow = date.today()
    if datenow > date_object:
        return False
    else:
        return True

def apology(message, code=400):
    return render_template("apology.html", top=code, bottom=message), code


def freerooms(typeofroom, datefrom, dateto):
    hotel_id = session["hotel_id"]
    datefrom_asked = datetime.strptime(datefrom, '%Y-%m-%d').date()
    dateto_asked = datetime.strptime(dateto, '%Y-%m-%d').date()
    reservedrooms = 0

    # See how many rooms the hotel have
    if typeofroom == "twobed":
        freerooms = int(db.execute("SELECT tworoom FROM hotels WHERE hotel_id = ?", hotel_id)[0]['tworoom'])
    if typeofroom == "threebed":
        freerooms = int(db.execute("SELECT threeroom FROM hotels WHERE hotel_id = ?", hotel_id)[0]['threeroom'])
    if typeofroom == "apartment":
        freerooms = int(db.execute("SELECT apartments FROM hotels WHERE hotel_id = ?", hotel_id)[0]['apartments'])

    #Get all reservation dates
    fromdate_reservations = db.execute("SELECT fromdate FROM reservations WHERE hotel_id = ? AND roomtype = ?", hotel_id, typeofroom)
    todate_reservations = db.execute("SELECT todate FROM reservations WHERE hotel_id = ? AND roomtype = ?", hotel_id, typeofroom)

    # see if dates overlap and count them
    for i in range(len(fromdate_reservations)):
        fromdate_reservation = datetime.strptime(fromdate_reservations[i]["fromdate"], '%Y-%m-%d').date()
        todate_reservation = datetime.strptime(todate_reservations[i]["todate"], '%Y-%m-%d').date()

        if  fromdate_reservation <= datefrom_asked <= todate_reservation or fromdate_reservation <= dateto_asked <= todate_reservation:
            reservedrooms += 1
        elif datefrom_asked <= fromdate_reservation and dateto_asked >= todate_reservation:
            reservedrooms += 1

    return freerooms - reservedrooms


def reservedrooms(typeofroom, datefrom, dateto):
    hotel_id = session["hotel_id"]
    datefrom_asked = datetime.strptime(datefrom, '%Y-%m-%d').date()
    dateto_asked = datetime.strptime(dateto, '%Y-%m-%d').date()
    reservedrooms = 0

    #Get all reservation dates
    fromdate_reservations = db.execute("SELECT fromdate FROM reservations WHERE hotel_id = ? AND roomtype = ?", hotel_id, typeofroom)
    todate_reservations = db.execute("SELECT todate FROM reservations WHERE hotel_id = ? AND roomtype = ?", hotel_id, typeofroom)
    length = len(fromdate_reservations)

    # see if dates overlap and count them
    for i in range(length):
        fromdate_reservation = datetime.strptime(fromdate_reservations[i]["fromdate"], '%Y-%m-%d').date()
        todate_reservation = datetime.strptime(todate_reservations[i]["todate"], '%Y-%m-%d').date()

        if  fromdate_reservation <= datefrom_asked <= todate_reservation or fromdate_reservation <= dateto_asked <= todate_reservation:
            reservedrooms += 1
        elif datefrom_asked <= fromdate_reservation and dateto_asked >= todate_reservation:
            reservedrooms += 1
    return reservedrooms

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("hotel_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        hotelname = request.form.get("hotelname")
        twopeople = request.form.get("twopeople")
        threepeople = request.form.get("threepeople")
        morepeople = request.form.get("morepeople")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmpass = request.form.get("confirmpass")

        # Validating input
        if not hotelname or not twopeople or not threepeople or not morepeople or not username or not password or not confirmpass or password != confirmpass:
            return apology("Invalid input")

        # Checking if username already exists
        rows = db.execute("SELECT * FROM hotels WHERE username = ?", request.form.get("username"))
        if len(rows) != 0:
            return apology("Username already exists try with something else")

        # Add the new user in the database
        db.execute("INSERT INTO hotels (username, hash, hotelname, tworoom, threeroom, apartments) VALUES (?, ?, ?, ?, ?, ?)", username, generate_password_hash(password), hotelname, twopeople, threepeople, morepeople)
        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check input
        if not username or not password:
            return apology("Invalid input")

        # Check password
        users = db.execute("SELECT * FROM hotels WHERE username = ?", request.form.get("username"))
        if not users:
            return apology("Wrong username")
        if not check_password_hash(users[0]['hash'], password):
            return apology("Wrong password")

        # Add session
        session["hotel_id"] = users[0]["hotel_id"]
        return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/reserve", methods= ["GET", "POST"])
@login_required
def reserve():
    if request.method == "GET":
        return render_template("reserve.html")
    if request.method == "POST":
        # When "post" get the number from the input and use it to print the next html page
        number = request.form.get("number")
        if not number:
            return apology("Invalid input")
        else:
            number = int(number)

        if number > 0 and number <= 6:
            return render_template("/reserve1.html", number=number)
        return apology("Number is not within the borders")


@app.route("/reserve1", methods= ["GET", "POST"])
@login_required
def reserve1():
    if request.method == "GET":
        return redirect("/reserve")
    if request.method == "POST":
        resname = request.form.get("resname")
        if not resname or resname == '':
            return apology("Please give reservation name")
        hotel_id = session["hotel_id"]
        room = []
        dateto = []
        datefrom = []

        #Didn`t find a way to use string variable to change the request.form.get() functions so I had
        #to do It the manual way. Maybe in next updates the code will be optimised so it is more readable
        a = request.form.get("operator0")
        b = request.form.get("dateto0")
        c = request.form.get("datefrom0")

        if a != None and b != None and c != None:
            if a != '':
                room.append(a)
            else: return apology("123")
            if b == '' or checkdate(b) == False or c == '' or checkdate(c) == False or b > c:
                return apology("Incorrect input")
            else:
                if freerooms(a, c, b) > 0:
                    dateto.append(b)
                    datefrom.append(c)

        a = request.form.get("operator1")
        b = request.form.get("dateto1")
        c = request.form.get("datefrom1")
        if a != None and b != None and c != None:
            if a != '':
                room.append(a)
            else: return apology("123")
            if b == '' or checkdate(b) == False or c == '' or checkdate(c) == False or b > c:
                return apology("Incorrect input")
            else:
                if freerooms(a, c, b) > 0:
                    dateto.append(b)
                    datefrom.append(c)

        a = request.form.get("operator2")
        b = request.form.get("dateto2")
        c = request.form.get("datefrom2")
        if a != None and b != None and c != None:
            if a != '':
                room.append(a)
            else: return apology("123")
            if b == '' or checkdate(b) == False or c == '' or checkdate(c) == False or b > c:
                return apology("Incorrect input")
            else:
                if freerooms(a, c, b) > 0:
                    dateto.append(b)
                    datefrom.append(c)

        a = request.form.get("operator3")
        b = request.form.get("dateto3")
        c = request.form.get("datefrom3")
        if a != None and b != None and c != None:
            if a != '':
                room.append(a)
            else: return apology("123")
            if b == '' or checkdate(b) == False or c == '' or checkdate(c) == False or b > c:
                return apology("Incorrect input")
            else:
                if freerooms(a, c, b) > 0:
                    dateto.append(b)
                    datefrom.append(c)

        a = request.form.get("operator4")
        b = request.form.get("dateto4")
        c = request.form.get("datefrom4")
        if a != None and b != None and c != None:
            if a != '':
                room.append(a)
            else: return apology("123")
            if b == '' or checkdate(b) == False or c == '' or checkdate(c) == False or b > c:
                return apology("Incorrect input")
            else:
                if freerooms(a, c, b) > 0:
                    dateto.append(b)
                    datefrom.append(c)

        a = request.form.get("operator5")
        b = request.form.get("dateto5")
        c = request.form.get("datefrom5")
        if a != None and b != None and c != None:
            if a != '':
                room.append(a)
            else: return apology("123")
            if b == '' or checkdate(b) == False or c == '' or checkdate(c) == False or b > c:
                return apology("Incorrect input")
            else:
                if freerooms(a, c, b) > 0:
                    dateto.append(b)
                    datefrom.append(c)

        a = request.form.get("operator6")
        b = request.form.get("dateto6")
        c = request.form.get("datefrom6")
        if a != None and b != None and c != None:
            if a != '':
                room.append(a)
            else: return apology("123")
            if b == '' or checkdate(b) == False or c == '' or checkdate(c) == False or b > c:
                return apology("Incorrect input")
            else:
                if freerooms(a, c, b) > 0:
                    dateto.append(b)
                    datefrom.append(c)


        for i in range(len(room)):
            db.execute("INSERT INTO reservations (hotel_id, resname, roomtype, fromdate, todate) VALUES (?, ?, ?, ?, ?)",hotel_id,  resname, room[i], dateto[i], datefrom[i])

        return redirect("/")


@app.route("/reservations")
@login_required
def reservations():
    hotel_id = session["hotel_id"]
    history = db.execute("SELECT * FROM reservations WHERE hotel_id = ?", hotel_id)

    return render_template("reservations.html", history = history)


@app.route("/check", methods=["GET", "POST"])
@login_required
def check():
    if request.method == "GET":
        return render_template("check.html")
    if request.method == "POST":
        typeofroom = request.form.get("operator")
        fromdate = request.form.get("fromdate")
        todate = request.form.get("todate")
        if checkdate(fromdate) == False or checkdate(todate) == False:
            return apology("Invalid input")
        if not typeofroom or not fromdate or not todate:
            return apology("Invalid input")

        answer = freerooms(typeofroom, fromdate, todate)
        return render_template("check.html", answer=answer)


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        hotel_id = session["hotel_id"]
        print(hotel_id)
        if not hotel_id:
            return redirect("/login")
        hotelname = db.execute("SELECT hotelname FROM hotels WHERE hotel_id = ?", hotel_id)
        if not hotelname:
            return redirect("/login")
        else:
            hotelname = hotelname[0]["hotelname"]
        info = db.execute("SELECT * FROM reservations WHERE hotel_id = ?", hotel_id)
        total = len(info)

        # Using datetime module to make the calculations with dates and the converting the dateobjects to strings
        today = date.today()
        today = today.strftime("%Y-%m-%d")
        behind = date.today() + relativedelta(months=-1)
        ahead = date.today() + relativedelta(months=+1)
        behind = behind.strftime("%Y-%m-%d")
        ahead = ahead.strftime("%Y-%m-%d")

        aheadres = reservedrooms("twobed", today, ahead) + reservedrooms("threebed", today, ahead) + reservedrooms("apartment", today, ahead)
        behindres = reservedrooms("twobed", behind, today) + reservedrooms("threebed", behind, today) + reservedrooms("apartment", behind, today)
        return render_template("index.html", behindres = behindres, aheadres = aheadres, info = info, total = total, hotelname = hotelname)

