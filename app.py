from flask import Flask, redirect, render_template, request, jsonify
import sqlite3

from functions import create_databases, fetch_therapy_data, generateImage, login_required, qotd
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

con = sqlite3.connect("mental.db", check_same_thread=False)
cur = con.cursor()

create_databases()

q = qotd()

current_username = ""

@app.route("/")
def home():
    return render_template("index.html", qu=q)

@app.route('/login', methods=['GET', 'POST'])
def login():
    current_username = ""
    if request.method == "POST":
        username = request.form.get("username").rstrip()
        password = request.form.get("password")

        if not (username and password): return "Fill out all fields"
        
        check = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()
        if not (check and check_password_hash(check[0][2], password)): return "Incorrect username or password"

        current_username = username
        print(current_username)
        return redirect("/")
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
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
    return render_template("register.html")


@app.route("/whiteboard")
def whiteboard():
    return render_template("whiteboard.html")

@app.route("/getImage", methods=['GET', 'POST'])
def get_image():
    if request.method == 'POST':
        story = request.form.get('story')
        image = generateImage(story, current_username)
        print(image)

        return render_template('whiteboard.html', story=story, image=image)
    print("NO IMAGE")
    return render_template('whiteboard.html')


@app.route('/therapy', methods=['POST'])
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