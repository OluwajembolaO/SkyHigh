from flask import Flask, redirect, render_template, request, session, jsonify, session
from flask_session import Session
import sqlite3

from functions import create_databases, fetch_therapy_data, generateImage, login_required, qotd
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

con = sqlite3.connect("goals.db", check_same_thread=False)
cur = con.cursor()


q = qotd()

@app.route("/")
@login_required
def home():
    return render_template("index.html", qu=q)

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username").rstrip()
        password = request.form.get("password")

        if not (username and password): return "Fill out all fields"
        check = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()
        if not (check and check_password_hash(check[0][2], password)): return "Incorrect username or password"

        session["user_id"] = check[0][0]
        return redirect("/")
    return render_template("login.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form.get("username").rstrip()
        password = request.form.get("password")
        confirmation = request.form.get("confirmpassword")

        if not (username and password and confirmation): return "Fill out all fields"
        if password != confirmation: return "Password does not match retyped password"

        try: cur.execute("INSERT INTO users (username, hash_password) VALUES (?, ?)", (username, generate_password_hash(password)))
        except sqlite3.IntegrityError: return "Username taken"

        con.commit()
        return redirect("/login")
    return render_template("signup.html")

@app.route("/video")
@login_required
def video():
    return render_template("video.html")

@app.route("/help")
@login_required
def help():
    return render_template("help.html")

@app.route('/therapy', methods=['POST'])
@login_required
def find_therapy():
    data = request.get_json()
    if data['location'] == "" or 'location' not in data:
        return jsonify({'error': 'Location is required.'}), 400

    location = data['location']

    therapies = fetch_therapy_data(location)

    if not therapies:
        return jsonify({'error': 'No therapists found nearby.'}), 404

    return jsonify(therapies)

if __name__ == '__main__':
    app.run(debug=True)