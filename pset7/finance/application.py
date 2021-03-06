import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, make_response
# url_for() added by me 201808112215 per Doug Lloyds flask video
# https://www.youtube.com/watch?v=0SQdkDpMzKE&list=PLXmMXHVSvS-CMpHUeyIeqzs3kl-tIG-8R
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd
import datetime

# Configure application
app = Flask(__name__)

# http://flask.pocoo.org/docs/1.0/quickstart/#sessions
# Set the secret key to some random bytes. Keep this really secret!
# $ python -c 'import os; print(os.urandom(24))'
app.secret_key = '\xcfP\x0cC\xb4\xc8\x9cL\xadG\xd4>\xbd:\x1e\x12\xd8\x07\xde\x9f\x06\x1189'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
# db = SQL("sqlite:////home/ubuntu/workspace/cs50/pset7/finance/finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    if(session["user_id"] is None):
        return render_template("login.html")

    user_id = session["user_id"]
    username = session["username"]

    portfolio = viewPortfolio()
    if len(portfolio) == 0:
        sumOfStocks = sumStocks()
        cash = getCashBalance()
        sumTotal = cash
    else:
        sumOfStocks = sumStocks()
        cash = getCashBalance()
        sumTotal = cash + sumOfStocks

    # add username and user_id for the Welcome message in navbar
    return render_template("index.html",
                           portfolio=portfolio,
                           sumOfStocks=sumOfStocks,
                           cash=cash,
                           sumTotal=sumTotal,
                           username=username,
                           user_id=user_id)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if(session["user_id"] is None):
        return render_template("login.html")

    user_id = session["user_id"]
    username = session["username"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Returns apology page if input is not valid
        # isValidInput()
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)

        if not request.form.get("shares"):
            return apology("must provide number of shares", 403)

        session["quote"] = lookup(request.form.get("symbol"))
        session["shares"] = int(request.form.get("shares"))

        if(session.get('quote') is None):
            print("invalid symbol")
            return apology("invalid symbol", 403)

        user_id = session["user_id"]
        cash = db.execute("SELECT cash FROM users WHERE id = :user_id",
                          user_id=session["user_id"])

        cash = float(cash[0]["cash"])
        print("cash == " + str(cash))

        price = session["quote"].get("price")
        shares = session["shares"]
        total = price * shares

        if(cash < total):
            return apology("Sorry, you don't have enough money for this trade.", 403)

        return render_template("confirm.html",
                               shares=session,
                               quote=session,
                               username=username,
                               user_id=user_id)

    # User reached route via GET (as by clicking a link or via redirect)
    # add username and user_id for the Welcome message in navbar
    else:
        return render_template("buy.html",
                               username=username,
                               user_id=user_id)


@app.route("/confirm", methods=["GET", "POST"])
@login_required
def confirm():
    """Confirm trade shares of stock"""

    if(session["user_id"] is None):
        return render_template("login.html")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        user_id = session["user_id"]
        username = session["username"]
        shares = session.get('shares')
        quote = session.get('quote')

        addTradeToDatabase(shares, quote, user_id)

        rows = viewPortfolio()
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    # add username and user_id for the Welcome message in navbar
    else:
        return render_template("buy.html",
                               username=username,
                               user_id=user_id)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # return apology("TODO")

    if(session["user_id"] is None):
        return render_template("login.html")

    user_id = session["user_id"]
    username = session["username"]

    user_id = session["user_id"]

    # Query database for view
    rows = db.execute("SELECT * FROM trades WHERE user_id = :user_id",
                      user_id=user_id)

    if len(rows) == 0:
        return apology("sorry, you have't bought or sold any stocks yet", 403)

    # add username and user_id for the Welcome message in navbar
    return render_template("history.html",
                           trades=rows,
                           username=username,
                           user_id=user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # give feedback to user with flash message
        flash('You were successfully logged in')

        # Redirect user to home page
        return redirect("/")  # change to / when finish testing /buy

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if(session["user_id"] is None):
        return render_template("login.html")

    user_id = session["user_id"]
    username = session["username"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)
        else:
            session["quote"] = lookup(request.form.get("symbol"))
            print("in quote():")
            print(session["quote"])

            if(session.get('quote') is None):
                print("invalid symbol")
                return apology("invalid symbol", 403)

            # add username and user_id for the Welcome message in navbar
            return render_template("quoted.html",
                                   quote=session,
                                   username=username,
                                   user_id=user_id)

    # User reached route via GET (as by clicking a link or via redirect)
    # add username and user_id for the Welcome message in navbar
    else:
        return render_template("quote.html",
                               username=username,
                               user_id=user_id)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Adapted from "/login" above
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 403)

        # Compare password and confirmation for equality
        if not request.form.get("password") == request.form.get("confirmation"):
            return apology("Sorry, passwords do not match.  Try again.", 403)

        # passed above tests so add name and password hash to database
        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for username used already
        # NOTE: this can be accomplished with keyword UNIQUE in db schema
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        if len(rows) > 0:
            return apology("Sorry, that username is already taken. Try again.", 403)

        # source https://docs.python.org/2/library/hashlib.html
        hash = generate_password_hash(password)
        check_hash = check_password_hash(hash, password)

        # source Zamylas walkthrough video 2 @ 2:27
        db.execute("INSERT INTO users (username, hash) \
        VALUES(:username, :hash)", username=request.form.get("username"), hash=hash)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # give feedback to user with flash message
        flash('You were successfully registered')

        # Redirect user to home page
        return redirect("/")

    # return apology("TODO")
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if(session["user_id"] is None):
        return render_template("login.html")

    user_id = session["user_id"]
    username = session["username"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Returns apology page if input is not valid
        # isValidInput()
        if not request.form.get("shares"):
            return apology("must provide number of shares", 403)

       # Ensure number of shares was submitted
        # elif not request.form.get("shares"):
        if request.form.get("shares") == " ":
            return apology("must provide number of shares", 403)

        symbol = request.form.get("symbol")
        session["quote"] = lookup(request.form.get("symbol"))
        # multiply shares sold by -1 reduces logic complications
        session["shares"] = int(request.form.get("shares")) * -1

        if(getNumSharesOwned(symbol) < abs(session["shares"])):
            return apology("Sorry, you don't have enough shares for this trade.", 403)

        # add username and user_id for the Welcome message in navbar
        return render_template("confirm.html",
                               shares=session,
                               quote=session,
                               username=username,
                               user_id=user_id)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        rows = {}
        portfolio = []

        # Query database for portfolio view
        rows = db.execute("SELECT * FROM portfolio WHERE user_id = :user_id",
                          user_id=user_id)

        for row in range(len(rows)):
            portfolio.append(rows[row]["symbol"])

        # add username and user_id for the Welcome message in navbar
        return render_template("sell.html",
                               portfolio=portfolio,
                               username=username,
                               user_id=user_id)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


# add transaction to atabase
@login_required
def addTradeToDatabase(shares, quote, user_id):

    # extract values out of session object
    user_id = session["user_id"]

    symbol = quote["symbol"]
    company_name = quote["name"]
    price = quote["price"]
    timestamp = quote["timestamp"]
    tradeTotal = shares * price

    # Query database for cash and caclulate cash balance after trade
    cash = getCashBalance() - tradeTotal

    # add trade to portfolio
    db.execute("INSERT INTO trades (user_id, shares, symbol, company_name, price, timestamp) \
        VALUES(:user_id, :shares, :symbol, :company_name, :price, :timestamp)", user_id=user_id, shares=shares, symbol=symbol, company_name=company_name, price=price, timestamp=timestamp)

    id = session["user_id"]
    db.execute("UPDATE users SET cash = :cash WHERE id = :id", id=id, cash=cash)

# retrieve portfolio view for display to index.html


@login_required
def viewPortfolio():

    user_id = session["user_id"]

    portfolio = {}

    # Query database for portfolio view
    rows = db.execute("SELECT * FROM portfolio WHERE user_id = :user_id",
                      user_id=user_id)

    if len(rows) == 0:
        print("\n rows == " + str(len(rows)))
    else:
        for row in range(len(rows)):
            session["quote"] = lookup(rows[row]["symbol"])  # get fresh data
            price = session["quote"].get("price")
            shares = rows[row]["sum(shares)"]
            if(int(shares) > 0):
                portfolio[rows[row]["symbol"]] = (
                    rows[row]["symbol"],
                    rows[row]["company_name"],
                    shares,
                    price,
                    shares * price)

    return portfolio


# add up the total of all positions
def sumStocks():

    sumStocks = 0
    user_id = session["user_id"]

    # Query database for portfolio
    trades = db.execute("SELECT * FROM trades WHERE user_id = :user_id",
                        user_id=user_id)

    portfolio = db.execute("SELECT * FROM portfolio WHERE user_id = :user_id",
                           user_id=user_id)

    if (len(trades) > 0):
        for row in range(len(trades)):
            session["quote"] = lookup(trades[row]["symbol"])  # get fresh data
            price = session["quote"].get("price")
            shares = trades[row]["shares"]
            sumStocks += shares * price

    return sumStocks


def getCashBalance():

    id = session["user_id"]

    # Query database for cash
    rows = db.execute("SELECT cash FROM users WHERE id = :id", id=id)

    cash = rows[0]["cash"]

    return cash


# get number of shares in portfolio
def getNumSharesOwned(symbol):

    user_id = session["user_id"]
    numShares = db.execute("SELECT * FROM portfolio WHERE user_id = :user_id and symbol = :symbol",
                           user_id=session["user_id"], symbol=symbol)

    numShares = int(numShares[0]["sum(shares)"])

    return numShares


def isValidInput():

    print("\n462. inside isValidInput()")

    # Ensure symbol was submitted
    if not request.form.get("symbol"):
        return apology("must provide symbol", 403)

    # Ensure number of shares was submitted
    if not request.form.get("shares"):
        return apology("must provide number of shares", 403)

    return True

# source http://flask.pocoo.org/docs/0.12/templating/#context-processors
# video https://www.youtube.com/watch?v=8qDdbcWmzCg


@app.context_processor
def utility_processor():
    def format_date(epoch):
        fmt = "%m-%d-%Y @ %-I:%M %p"
        t = datetime.datetime.fromtimestamp(float(epoch)/1000.)
        print("490. j_date == ")
        print(t.strftime(fmt))
        return t.strftime(fmt)
    return(dict(format_date=format_date))


@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():

    if(session["user_id"] is None):
        return render_template("login.html")

    id = session["user_id"]
    user_id = id
    username = session["username"]

    timestamp = datetime.datetime.now().timestamp()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure amount was submitted
        if not request.form.get("amount"):
            return apology("must provide amount", 403)
        elif(int(request.form.get("amount")) < 0):
            return apology("amount must be > 0", 403)
        else:
            session["amount"] = request.form.get("amount")

            amount = float(session.get('amount'))

            # add deposit to cashInOut
            db.execute("INSERT INTO cashInOut (user_id, amount, timestamp) \
                VALUES (:user_id, :amount, :timestamp)", user_id=user_id, amount=amount, timestamp=timestamp)

            # Query database for cash
            rows = db.execute("SELECT cash FROM users WHERE id = :id", id=id)

            # if len(rows) == 0:
            #     return apology("sorry, you have no cash", 403)

            cash = rows[0]["cash"]
            cash = cash + float(amount)

            db.execute("UPDATE users SET cash = :cash WHERE id = :id", id=id, cash=cash)

            return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
        # add username and user_id for the Welcome message in navbar
    else:
        return render_template("deposit.html",
                               username=username,
                               user_id=id)


@app.route("/withdraw", methods=["GET", "POST"])
@login_required
def withdraw():
    if(session["user_id"] is None):
        return render_template("login.html")

    id = session["user_id"]
    user_id = id
    username = session["username"]

    timestamp = datetime.datetime.now().timestamp()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure amount was submitted
        if not request.form.get("amount"):
            return apology("must provide amount", 403)
        elif(int(request.form.get("amount")) < 0):
            return apology("amount must be > 0", 403)
        else:
            session["amount"] = request.form.get("amount")

            amount = float(session.get('amount'))

            # determine if available cash > withdraw amount
            cashBalance = getCashBalance()
            if(cashBalance < amount):
                return apology("sorry, you don't have enough cash to withdraw that amount", 403)

            # subtract withdraw to cashInOut
            amount = amount * -1
            db.execute("INSERT INTO cashInOut (user_id, amount, timestamp) \
                VALUES (:user_id, :amount, :timestamp)", user_id=user_id, amount=amount, timestamp=timestamp)

            # Query database for cash
            rows = db.execute("SELECT cash FROM users WHERE id = :id", id=id)

            # if len(rows) == 0:
            #     return apology("sorry, you have no cash", 403)

            cash = rows[0]["cash"]
            cash = cash + float(amount)

            db.execute("UPDATE users SET cash = :cash WHERE id = :id", id=id, cash=cash)

            return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
        # add username and user_id for the Welcome message in navbar
    else:
        return render_template("withdraw.html",
                               username=username,
                               user_id=id)
