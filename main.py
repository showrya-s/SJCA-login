from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key_here"  # Change to something strong!

# ---- Dummy user database with hashed passwords ----
users = {
    "student1": [generate_password_hash("pass123"), "student"],
    "teacher1": [generate_password_hash("pass456"), "teacher"],
    "headmaster": [generate_password_hash("admin123"), "head"]
}


@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        if username in users and check_password_hash(users[username][0], password):
            session["username"] = username
            session["role"] = users[username][1]
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    success = None

    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]
        role = request.form["role"]

        if username in users:
            error = "Username already exists."
        else:
            users[username] = [generate_password_hash(password), role]
            success = "Account created successfully! You can now login."
    
    return render_template("register.html", error=error, success=success)


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    main_site_url = "https://sjca-iq3k.onrender.com/"  # Replace with your main site
    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"],
        main_site_url=main_site_url
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

