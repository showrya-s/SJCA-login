from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")  # Use env in production

# --- Database setup ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    section = db.Column(db.String(50), nullable=False, default="grade 1")

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    section = db.Column(db.String(50), nullable=False, default="grade 1")

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)

# --- Create tables and default accounts ---
with app.app_context():
    db.create_all()

    # Default admin account
    if not User.query.filter_by(username="admin").first():
        hashed_pw = generate_password_hash("admin123")
        admin_user = User(username="admin", password=hashed_pw, role="head", section="all")
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin account created: username='admin', password='admin123'")

    # Default Grade 5 student account
    if not User.query.filter_by(username="jaitya reddy").first():
        hashed_pw = generate_password_hash("grade5pass")
        grade5_student = User(username="jaitya reddy", password=hashed_pw, role="student", section="grade 5")
        db.session.add(grade5_student)
        db.session.commit()
        print("Default Grade 5 student account created: username='Jaitya Reddy', password='grade5pass', section='Grade 5'")

# --- Routes ---
@app.route("/")
def home():
    return redirect(url_for("dashboard") if "username" in session else url_for("login"))

# --- Login ---
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["username"] = user.username
            session["role"] = user.role
            session["section"] = user.section
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password."
    return render_template("login.html", error=error)

# --- Register ---
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    success = None
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]
        role = request.form["role"]
        section = request.form.get("section", "grade 1")
        if User.query.filter_by(username=username).first():
            error = "Username already exists."
        else:
            hashed_pw = generate_password_hash(password)
            new_user = User(username=username, password=hashed_pw, role=role, section=section)
            db.session.add(new_user)
            db.session.commit()
            success = "Account created successfully! You can now login."
    return render_template("register.html", error=error, success=success)

# --- Dashboard ---
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    # Assignments, notifications filtered by section
    assignments = Assignment.query.filter_by(section=session.get("section")).all()
    notifications = Notification.query.all()  # Notifications are for whole academy

    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"],
        section=session.get("section"),
        assignments=assignments,
        notifications=notifications
    )

# --- Add Assignment ---
@app.route("/add_assignment", methods=["POST"])
def add_assignment():
    if "username" not in session:
        return redirect(url_for("login"))
    if session["role"] in ["teacher", "head"]:
        text = request.form["text"].strip()
        section = request.form.get("section", "grade 1")
        if text:
            db.session.add(Assignment(text=text, section=section))
            db.session.commit()
    return redirect(url_for("dashboard"))

# --- Add Notification ---
@app.route("/add_notification", methods=["POST"])
def add_notification():
    if "username" not in session or session["role"] not in ["teacher", "head"]:
        return redirect(url_for("dashboard"))
    title = request.form["title"].strip()
    text = request.form["text"].strip()
    if title and text:
        db.session.add(Notification(title=title, text=text))
        db.session.commit()
    return redirect(url_for("dashboard"))

# --- Delete Assignment ---
@app.route("/delete_assignment/<int:id>", methods=["POST"])
def delete_assignment(id):
    if "username" not in session or session["role"] not in ["teacher", "head"]:
        return redirect(url_for("dashboard"))
    assignment = Assignment.query.get_or_404(id)
    db.session.delete(assignment)
    db.session.commit()
    return redirect(url_for("dashboard"))

# --- Delete Notification ---
@app.route("/delete_notification/<int:id>", methods=["POST"])
def delete_notification(id):
    if "username" not in session or session["role"] not in ["teacher", "head"]:
        return redirect(url_for("dashboard"))
    note = Notification.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for("dashboard"))

# --- Logout ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- Run App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

