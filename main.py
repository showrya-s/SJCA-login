from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change to a strong secret key!

# Dummy user database: username -> [password, role]
users = {
    "student1": ["pass123", "student"],
    "teacher1": ["pass456", "teacher"],
    "headmaster": ["admin123", "head"]
}

@app.route('/')
def home():
    if 'username' in session:
        main_site_url = "https://sjca-iq3k.onrender.com/"  # Your main site URL here
        return render_template('dashboard.html',
                               username=session['username'],
                               role=session['role'],
                               main_site_url=main_site_url)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username][0] == password:
            session['username'] = username
            session['role'] = users[username][1]
            return redirect(url_for('home'))
        else:
            error = "Invalid username or password."
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Optional: protected pages
@app.route('/teacher-area')
def teacher_area():
    if 'role' in session and session['role'] in ['teacher', 'head']:
        return f"Welcome {session['username']} to the Teacher/Headmaster area."
    return redirect(url_for('home'))

@app.route('/student-area')
def student_area():
    if 'role' in session and session['role'] == 'student':
        return f"Welcome {session['username']} to the Student area."
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
