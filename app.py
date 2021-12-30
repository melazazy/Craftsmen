import os
from cs50 import SQL

from flask import Flask, render_template, request, redirect, session, flash, url_for, g
from flask_session import Session
from flask_mail import Mail, Message

from module import login_required

# from helper import login_required

from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
mail = Mail(app)

# app.config["SECRET_KEY"] = "mysecretkey"


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "craftsmen.contact"
app.config["MAIL_PASSWORD"] = "#TestPass@"
mail = Mail(app)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# list of Avialable Services
SERVICES = [
    "service1",
    "service2",
    "service3",
    "service4",
    "service5",
    "service6",
]

# Connect crafts sql database CS50 Library
db = SQL("sqlite:///crafts.db")

# Index Page
@app.route("/")
def index():
    return render_template("index.html")


# Register Page
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()
    msg = ""
    if request.method == "POST":
        # form = request.form("name")
        if "craft" in request.form:
            if request.form.get("password") != request.form.get("confirmation"):
                flash("Not Matched password!!", category="error")
                return render_template("/register.html", services=SERVICES)
            else:
                # hashed_pass = generate_password_hash(request.form.get('password'))
                hashed_pass = generate_password_hash(request.form.get("password"))
                NAME = request.form.get("name")
                MAIL = request.form.get("mail")
                try:
                    db.execute(
                        "INSERT INTO crafts (name, e_mail, hash_pass) VALUES (?, ?, ?)",
                        NAME,
                        MAIL,
                        hashed_pass,
                    )
                    flash("Good its Done!!!!!!", category="succ")
                    return redirect("/login")
                except:
                    flash("Mail Already Exist!!", category="error")
                    return render_template("/register.html", services=SERVICES)
        else:
            if request.form.get("password") != request.form.get("confirmation"):
                flash("Not Matched password!!", category="error")
                return render_template("/register.html", services=SERVICES)
            else:
                # hashed_pass = generate_password_hash(request.form.get('password'))
                hashed_pass = generate_password_hash(request.form.get("password"))
                try:
                    db.execute(
                        "INSERT INTO clients (name, mail, hash_pass) VALUES (?, ?, ?)",
                        request.form.get("name"),
                        request.form.get("mail"),
                        hashed_pass,
                    )
                    return redirect("/")
                except:
                    flash("Mail Already Exist!!", category="error")
                    return render_template("/register.html", services=SERVICES)
    else:
        return render_template("register.html", services=SERVICES)


# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if "craft" in request.form:
            rows = db.execute(
                "SELECT * FROM crafts WHERE e_mail = ?",
                request.form.get("mail"),
            )
            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(
                rows[0]["hash_pass"], request.form.get("password")
            ):
                flash("invalid username and/or password", category="error")
                return render_template("login.html")

            # Remember which user has logged in
            session["user_id"] = rows[0]["cid"]
            return redirect("/")
        elif "client" in request.form:
            rows = db.execute(
                "SELECT * FROM clients WHERE mail = ?", request.form.get("mail")
            )
            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(
                rows[0]["hash_pass"], request.form.get("password")
            ):
                flash("invalid username and/or password", category="error")
                return render_template("login.html")

            # Remember which user has logged in
            session["user_id"] = rows[0]["cid"]
            return redirect("/")
    else:
        return render_template("login.html")


# Search Guest Page
@app.route("/guest")
def guest():
    session.clear()
    return render_template("search.html", services=SERVICES)


# Profile Page
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]
    if request.method == "GET":
        # CHECK if user craftsman or client
        # By Check if the 2nd letter is R --> cRaft or L -->cLient
        if user_id[1] == "R":
            # CRAFTSMAN
            cr_id = db.execute("SELECT * FROM crafts WHERE cid = ? ", user_id)[0][
                "craft_id"
            ]
            user = db.execute("SELECT * FROM crafts WHERE cid = ? ", user_id)
            rows = db.execute(
                "SELECT offers.* ,pending.status,pending.id ,COUNT(pending.serv_id) AS total FROM offers LEFT JOIN pending ON offers.offer_id = pending.serv_id WHERE  offers.cr_id = ? GROUP BY offers.service",
                cr_id,
            )
            list = db.execute(
                "SELECT pending.id,pending.status,pending.service,pending.req_id,pending.cl_id,pending.cr_id,pending.type, clients.client_id ,clients.name ,clients.mail FROM pending JOIN clients ON clients.client_id = pending.cl_id LEFT JOIN offers ON offers.offer_id = pending.serv_id WHERE pending.cr_id=? AND pending.type=?",
                cr_id,
                "offer",
            )
            return render_template("crprofile.html", rows=rows, user=user, list=list)
        elif user_id[1] == "L":
            # CLIENT
            cl_id = db.execute("SELECT * FROM clients WHERE cid = ? ", user_id)[0][
                "client_id"
            ]
            user = db.execute("SELECT * FROM clients WHERE cid = ? ", user_id)

            # rows = db.execute("SELECT * FROM requests WHERE c_id = ? ", l_id)
            rows = db.execute(
                "SELECT requests.* ,pending.status,pending.id ,COUNT(pending.req_id) AS total FROM requests LEFT JOIN pending ON requests.request_id = pending.req_id WHERE  requests.c_id = ? GROUP BY requests.service",
                cl_id,
            )
            list = db.execute(
                "SELECT pending.id,pending.status,pending.service,pending.serv_id,pending.cl_id,pending.cr_id,pending.type,\
                     crafts.craft_id ,crafts.name ,crafts.e_mail FROM pending\
                        LEFT JOIN crafts ON crafts.craft_id = pending.cr_id \
                        LEFT JOIN requests ON requests.request_id = pending.req_id\
                        WHERE pending.cl_id=? AND pending.type=?",
                cl_id,
                "request",
            )
            print("Rows")
            print(len(rows))
            print(str(rows))
            print("LIST")
            print(len(list))
            print(str(list))

            return render_template("clprofile.html", rows=rows, user=user, list=list)
        else:
            return "Some Thing Wrong!!!"
    else:
        # if user_id[1] == "R":
        if "client" in request.form:
            return render_template("add_request.html", services=SERVICES)
        # elif user_id[1] == "L":
        if "craft" in request.form:
            return render_template("add_service.html", services=SERVICES)
        else:
            return "Some Thing Wrong!!!!"


# Signout Link
@app.route("/logout")
@login_required
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


# Client Add Requests Button
@app.route("/add_request", methods=["GET", "POST"])
@login_required
def clprofil():
    user_id = session["user_id"]
    if request.method == "POST":
        service = request.form.get("services")
        ftime = request.form.get("ftime")
        ttime = request.form.get("ttime")
        country = request.form.get("country")
        state = request.form.get("state")
        city = request.form.get("city")
        price = request.form.get("price")
        notes = request.form.get("notes")
        contact = request.form.get("contact")
        id = db.execute("SELECT * FROM clients WHERE cid = ? ", user_id)[0]["client_id"]
        try:
            db.execute(
                "INSERT INTO requests (c_id, service, time_from,time_to,price,country,state,city,notes,contact) VALUES (?, ?, ?, ?, ?, ?,?,?,?,?)",
                id,
                service,
                ftime,
                ttime,
                price,
                country,
                state,
                city,
                notes,
                contact,
            )
            return redirect("/")
        except:
            return "NOTHING INSERT IN DATABASE"


# Craftsman Add Services Button
@app.route("/add_service", methods=["GET", "POST"])
@login_required
def crprofil():
    user_id = session["user_id"]
    if request.method == "POST":
        service = request.form.get("services")
        ftime = request.form.get("ftime")
        ttime = request.form.get("ttime")
        country = request.form.get("country")
        state = request.form.get("state")
        city = request.form.get("city")
        price = request.form.get("price")
        notes = request.form.get("notes")
        contact = request.form.get("contact")
        id = db.execute("SELECT * FROM crafts WHERE cid = ? ", user_id)[0]["craft_id"]
        try:
            db.execute(
                "INSERT INTO offers (cr_id, service, time_from, time_to, country, state, city,price,notes,contact) VALUES (?, ?,?, ?, ?, ?,? ,?,?,?)",
                id,
                service,
                ftime,
                ttime,
                country,
                state,
                city,
                price,
                notes,
                contact,
            )
            flash("GOOOD ", "succ")
            return redirect("/profile")
        except:
            return "NOTHING INSERT IN DATABASE Services"
    else:
        return render_template("crprofil.html")


# Search Page
@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "GET":
        return render_template("search.html", services=SERVICES)

    elif request.method == "POST":
        type = request.form.get("search-radio")
        service = request.form.get("services")
        # IF DB == OFFERS
        if type == "option1":
            servid = db.execute(
                "SELECT offers.* ,crafts.name FROM offers INNER JOIN crafts ON Offers.cr_id == crafts.craft_id WHERE offers.service = ?",
                service,
            )
            return render_template(
                "search.html",
                show="show_table",
                serv=servid,
                services=SERVICES,
            )
        # IF DB == REQUESTS
        elif type == "option2":
            reqs = db.execute(
                "SELECT requests.* ,clients.name FROM requests INNER JOIN clients ON requests.c_id == clients.client_id WHERE requests.service = ?",
                service,
            )
            return render_template(
                "search.html",
                show="show_table",
                req=reqs,
                services=SERVICES,
            )

        # IF DB == OFFERS AND REQUESTS
        elif type == "option3":
            servid = db.execute(
                "SELECT offers.* ,crafts.name FROM offers INNER JOIN crafts ON Offers.cr_id == crafts.craft_id WHERE offers.service = ?",
                service,
            )
            reqs = db.execute(
                "SELECT requests.* ,clients.name FROM requests INNER JOIN clients ON requests.c_id == clients.client_id WHERE requests.service = ?",
                service,
            )

            return render_template(
                "search.html",
                show="show_table",
                serv=servid,
                req=reqs,
                services=SERVICES,
            )
        else:
            return render_template("search.html", services=SERVICES)


# Insert Services in penndig table
@app.route("/reqserv", methods=["POST"])
def accserv():
    # Insert data in penndig from offers Table
    user_id = session["user_id"]
    off_id = request.form.get("offid")
    # service = request.form.get("offid")
    data = db.execute(
        "SELECT * FROM offers  WHERE offer_id = ?",
        off_id,
    )
    user = db.execute("SELECT * FROM clients  WHERE cid = ?", user_id)[0]["client_id"]
    db.execute(
        "INSERT INTO pending (serv_id, service ,cl_id,cr_id,type) VALUES (?,?, ?,?,?)",
        data[0]["offer_id"],
        data[0]["service"],
        user,
        data[0]["cr_id"],
        "offer",
    )
    flash("Service Pending.....!!", category="succ")
    return render_template("search.html", services=SERVICES)

    # except:
    #     flash("Please login!!", category="error")
    #     return render_template("search.html", services=SERVICES)


# Insert Requests in penndig table
@app.route("/acceptreq", methods=["POST"])
def accreq():
    # Insert data in penndig from requests Table
    user_id = session["user_id"]
    req_id = request.form.get("reqid")
    data = db.execute(
        "SELECT * FROM requests  WHERE request_id = ?",
        req_id,
    )
    id = db.execute("SELECT * FROM crafts WHERE cid = ?", user_id)[0]["craft_id"]
    db.execute(
        "INSERT INTO pending (req_id, service,cl_id, cr_id,type) VALUES (?,?,?, ?,?)",
        data[0]["request_id"],
        data[0]["service"],
        data[0]["c_id"],
        id,
        "request",
    )
    flash("Request Are Pending...!", category="succ")
    return render_template("search.html", services=SERVICES)


# Edit User Profile
@app.route("/editpro", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "POST":
        user_id = session["user_id"]
        if "R" == user_id[1]:
            cid = request.form.get("cid")
            name = request.form.get("name")
            country = request.form.get("country")
            state = request.form.get("state")
            city = request.form.get("city")
            db.execute(
                "UPDATE crafts SET name=?,country=?, state=?,city=? WHERE cid=? ",
                name,
                country,
                state,
                city,
                cid,
            )
            return redirect("\profile")
        else:
            cid = request.form.get("cid")
            name = request.form.get("name")
            db.execute(
                "UPDATE clients SET name=? WHERE cid=? ",
                name,
                cid,
            )
            return redirect("\profile")


# Requests Page in craftsman Profile
@app.route("/requests", methods=["GET", "POST"])
@login_required
def requests():
    user_id = session["user_id"]
    print(user_id)
    if request.method == "GET":
        # Craftsman
        user = db.execute("SELECT * FROM crafts  WHERE cid = ?", user_id,)[
            0
        ]["craft_id"]
        cr_pending_data = db.execute(
            "SELECT pending.*,clients.name FROM pending \
            LEFT JOIN clients ON pending.cl_id==clients.client_id \
            LEFT JOIN requests ON pending.req_id==requests.request_id\
            WHERE pending.cr_id = ? AND pending.type =? ",
            user,
            "request",
        )
        # rows = db.execute(
        #     "SELECT offers.* ,COUNT(pending.serv_id) AS total FROM offers LEFT JOIN pending ON offers.offer_id = pending.serv_id WHERE offers.cr_id = ? GROUP BY offers.offer_id ",
        #     cr_id,
        # )
        print("user: ")
        print(user)
        print("ROWS: ")
        print(type(cr_pending_data))
        print(str(cr_pending_data))

        return render_template("requests.html", pdata=cr_pending_data)


# Services page in Client profile
@app.route("/services", methods=["GET", "POST"])
@login_required
def services():
    user_id = session["user_id"]
    if request.method == "GET":
        # client
        user = db.execute("SELECT * FROM clients  WHERE cid = ?", user_id,)[
            0
        ]["client_id"]
        cl_pending_data = db.execute(
            "SELECT pending.*,crafts.name FROM pending \
            LEFT JOIN crafts ON pending.cr_id==crafts.craft_id \
            LEFT JOIN offers ON pending.req_id==offers.offer_id\
            WHERE pending.cl_id = ? AND pending.type =? ",
            user,
            "offer",
        )
        # cr_accepted_data = db.execute("SELECT ")
        print("Services")
        print(type(cl_pending_data))
        print(str(cl_pending_data))

        return render_template("services.html", pdata=cl_pending_data)


# Approval Or Reject Pending Requests
@app.route("/pendreq", methods=["GET", "POST"])
def cr_editing():
    if request.method == "POST":
        if request.form["action"] == "approve":
            id = request.form.get("id")
            db.execute("UPDATE pending SET status=? WHERE id=? ", 1, id)
            flash("Request Approved", category="succ")
            return redirect("/profile")
        elif request.form["action"] == "reject":
            id = request.form.get("id")
            db.execute("DELETE FROM pending WHERE id =? ", id)
            flash("Request Reject", category="succ")
            return redirect("/profile")
    else:
        return redirect("/profile")


# Approval Or Reject Pending Services
@app.route("/pendacc", methods=["GET", "POST"])
def cl_editing():
    if request.method == "POST":
        if request.form["action"] == "approve":
            id = request.form.get("id")
            db.execute("UPDATE pending SET status=? WHERE id=? ", 1, id)
            flash("Request Approved", category="succ")
            return redirect("/profile")
        elif request.form["action"] == "reject":
            id = request.form.get("id")
            db.execute("DELETE FROM pending WHERE id =? ", id)
            flash("Request Reject", category="succ")
            return redirect("/profile")
    else:
        return redirect("/profile")


# Contact Form Page
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("txtName")
        # email = "mazaz52@gmail.com]"
        email = request.form.get("txtEmail")
        phone = request.form.get("txtPhone")
        text = request.form.get("txtMsg")

        # flask-mail.Message(subject, recipients, body, html, sender, cc, bcc, reply-to, date, charset, extra_headers, mail_options, rcpt_options)
        print(name)
        print(email)
        print(phone)
        print(text)
        message = Message(
            subject="Contact Form ",
            recipients=[email],
            sender=app.config.get("MAIL_USERNAME"),
        )
        mail.send(message)
        flash("Thanks For Your Message", "succ")
        return redirect("/")
    else:
        return render_template("contact.html")
