from flask import Flask, render_template, request, redirect, url_for, session
import pymysql
from confi import config

app = Flask(__name__)
app.config.from_object(config)
app.secret_key = app.config["SECRET_KEY"]

users = {}  #this will take one user in a session

def get_db_connection():
    return pymysql.connect(
        host= app.config["MY_HOST"],
        user = app.config["MY_USER"],
        password = app.config["MY_PASSWORD"],
        database = app.config["MY_DATABSE"],
        port = app.config["MY_PORT"]
    )

@app.route("/")
def home():
    return redirect(url_for("index"))

@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u in users:
            return render_template("register.html", msg="User exists!")

        users[u] = p
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if users.get(u) == p:
            session["user"] = u
            return redirect(url_for("dashboard"))

        return render_template("login.html", msg="Invalid login!")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)