from datetime import datetime
from flask import Flask, redirect, render_template, request, jsonify, session
from flask_session import Session
from profanity import profanity
import sqlite3
import time

from functions import create_databases, fetch_therapy_data, generateImage, login_required, currenttime, qotd
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# timeout=100 because image ai would take so long the database would lock itself
con = sqlite3.connect(
    "mental.db", 
    check_same_thread=False, 
    timeout=100
)
cur = con.cursor()
create_databases()


@app.route('/details', methods=['POST'])
@login_required
def details():
    data = request.get_json()
    if not data: return jsonify({'error': 'no data'})
    url = data['url']
    if not url: return jsonify({'error': 'no url'})
    
    image_id = cur.execute('''
        SELECT id FROM image_details 
        WHERE id = (
            SELECT id FROM images WHERE url = ?
        )
    ''', (url,)).fetchone()[0]
    if not image_id: return jsonify({'error': 'not found'})

    user_id = session["user_id"]

    viewed = cur.execute("SELECT user_id FROM views WHERE id = ?", (image_id,)).fetchall()
    viewed = any(user_id == viewers[0] for viewers in viewed)
    if not viewed: 
        cur.execute("INSERT INTO views VALUES (?, ?)", (image_id, user_id))
        cur.execute("UPDATE image_details SET views = views + 1 WHERE id = ?", (image_id,))
    
    liked = cur.execute("SELECT user_id FROM likes WHERE id = ?", (image_id,)).fetchall()
    liked = any(user_id == likers[0] for likers in liked)
    
    con.commit()

    image_details = cur.execute('''
        SELECT views, likes, comments FROM image_details 
        WHERE id = ?
    ''', (image_id,)).fetchone()

    return jsonify({
        'views': image_details[0],
        'likes': image_details[1],
        'comments': image_details[2],
        'liked': liked
    })


@app.route('/therapy', methods=['POST'])
@login_required
def find_therapy():
    data = request.get_json()

    if data['location'] == "" or 'location' not in data: 
        return jsonify({'error': 'Location is required.'}), 400
    location = data['location']

    therapies = fetch_therapy_data(location)
    if not therapies: return jsonify({'error': 'No therapists found nearby.'}), 404

    return jsonify(therapies)


@app.route('/gallery', methods=['GET', 'POST'])
@login_required
def gallery():
    if request.method == "POST":
        search_for = request.form.get("search")
        sort_by = request.form.get("current")
        actual = search_for[0:len(search_for)-4]
        type = search_for[len(search_for)-4:]

        data = ""
        match sort_by:
            case "Newest":
                if type == "user":
                    data = cur.execute('''
                        SELECT url, description, date FROM images
                        WHERE user_id IN (
                            SELECT id FROM users
                            WHERE username LIKE ?
                        )
                        ORDER BY date DESC
                    ''', (f"%{actual}%",)).fetchall()
                else:
                    data = cur.execute('''
                        SELECT url, description, date FROM images
                        WHERE description LIKE ?
                        ORDER BY date DESC
                    ''', (f"%{actual}%",)).fetchall()
            case "Oldest":
                if type == "user":
                    data = cur.execute('''
                        SELECT url, description, date FROM images
                        WHERE user_id IN (
                            SELECT id FROM users
                            WHERE username LIKE ?
                        )
                    ''', (f"%{actual}%",)).fetchall()
                else:
                    data = cur.execute('''
                        SELECT url, description, date FROM images
                        WHERE description LIKE ?
                    ''', (f"%{actual}%",)).fetchall()
            case "Views":
                if type == "user":
                    data = cur.execute('''
                        SELECT url, description, date FROM images
                        JOIN image_details ON image_details.id = images.user_id
                        WHERE user_id IN (
                            SELECT id FROM users
                            WHERE username LIKE ?
                        )
                        ORDER BY image_details.views DESC
                    ''', (f"%{actual}%",)).fetchall()
                else:
                    data = cur.execute('''
                        SELECT url, description, date FROM images
                        JOIN image_details ON image_details.id = images.user_id
                        WHERE description LIKE ?
                        ORDER BY image_details.views DESC
                    ''', (f"%{actual}%",)).fetchall()
            case "Likes":
                if type == "user":
                    data = cur.execute('''
                        SELECT url, description, date FROM images
                        JOIN image_details ON image_details.id = images.user_id
                        WHERE user_id IN (
                            SELECT id FROM users
                            WHERE username LIKE ?
                        )
                        ORDER BY image_details.likes DESC
                    ''', (f"%{actual}%",)).fetchall()
                else:
                    data = cur.execute('''
                        SELECT url, description, date FROM images
                        JOIN image_details ON image_details.id = images.user_id
                        WHERE description LIKE ?
                        ORDER BY image_details.likes DESC
                    ''', (f"%{actual}%",)).fetchall()
            case "Comments":
                if type == "user":
                    data = cur.execute('''
                        SELECT url, description, date FROM images
                        JOIN image_details ON image_details.id = images.user_id
                        WHERE user_id IN (
                            SELECT id FROM users
                            WHERE username LIKE ?
                        )
                        ORDER BY image_details.comments DESC
                    ''', (f"%{actual}%",)).fetchall()
                else:
                    data = cur.execute('''
                        SELECT url, description, date FROM images
                        JOIN image_details ON image_details.id = images.user_id
                        WHERE description LIKE ?
                        ORDER BY image_details.comments DESC
                    ''', (f"%{actual}%",)).fetchall()
            case "Username":
                if type == "user":
                    data = cur.execute('''
                        SELECT url, description, date FROM images
                        JOIN users ON users.id = images.user_id
                        WHERE user_id IN (
                            SELECT id FROM users
                            WHERE username LIKE ?
                        )
                        ORDER BY users.username
                    ''', (f"%{actual}%",)).fetchall()
                else:
                    data = cur.execute('''
                        SELECT url, description, date FROM images
                        JOIN users ON users.id = images.user_id
                        WHERE description LIKE ?
                        ORDER BY users.username
                    ''', (f"%{actual}%",)).fetchall()
            case "Description":
                if type == "user":
                    data = cur.execute('''
                        SELECT url, description, date FROM images
                        WHERE user_id IN (
                            SELECT id FROM users
                            WHERE username LIKE ?
                        )
                        ORDER BY description
                    ''', (f"%{actual}%",)).fetchall()
                else:
                    data = cur.execute('''
                        SELECT url, description, date FROM images
                        WHERE description LIKE ?
                        ORDER BY description
                    ''', (f"%{actual}%",)).fetchall()
            case _: 
                return render_template("error.html", error="Stop html hacking pleasease")
        
        return render_template("gallery.html", data=data)
    data = cur.execute('''
        SELECT url, description, date FROM images
        ORDER BY date DESC
    ''').fetchall()
    return render_template("gallery.html", data=data)


@app.route("/")
@login_required
def home():
    username = cur.execute("SELECT username FROM users WHERE id = ?", 
                           (session["user_id"],)).fetchone()
    if not username: return redirect("/login")

    q = qotd()
    if not q: return render_template("error.html", error="Sorry! Something is wrong with the quote API!")

    return render_template("index.html", qu=q, user=username[0])


@app.route('/likes', methods=['POST'])
@login_required
def likes():
    data = request.get_json()
    if not data: return jsonify({'error': 'no data'})
    url = data['url']
    if not url: return jsonify({'error': 'no url'})
    inner = data['inner']
    if not inner: jsonify({'error': 'html hacking?'})

    print(inner)
    image_id = cur.execute('''
        SELECT id FROM image_details 
        WHERE id = (
            SELECT id FROM images WHERE url = ?
        )
    ''', (url,)).fetchone()[0]

    if inner == "<i class=\"fa-regular fa-heart\"></i>":
        cur.execute("UPDATE image_details SET likes = likes + 1 WHERE id = ?", (image_id,))
        cur.execute("INSERT INTO likes VALUES (?, ?)", (image_id, session["user_id"]))
        type = "not_pressed"
    elif inner == "<i class=\"fa-solid fa-heart\"></i>":
        cur.execute("UPDATE image_details SET likes = likes - 1 WHERE id = ?", (image_id,))
        cur.execute("DELETE FROM likes WHERE id = ? AND user_id = ?", (image_id, session["user_id"]))
        type = "pressed"
        
    con.commit()
    likes_count = cur.execute("SELECT likes FROM image_details WHERE id = ?", (image_id,)).fetchone()[0]

    return jsonify({
        'likes': likes_count,
        'type' : type
    })


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username").rstrip()
        password = request.form.get("password")

        if not (username and password): 
            return render_template("error.html", error="Fill out all required fields!")

        check = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()
        if not (check and check_password_hash(check[0][2], password)): 
            return render_template("error.html", error="Incorrect username or password!")

        session["user_id"] = check[0][0]
        return redirect("/")
    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get("username").rstrip()
        password = request.form.get("password")
        confirmation = request.form.get("confirmpassword")

        if not (username and password and confirmation): 
            return render_template("error.html", error="Fill out all required fields!")
        if len(username) > 25: 
            return render_template("error.html", error="Username exceeds 25 characters!")
        if profanity.contains_profanity(username): 
            return render_template("error.html", error="Username likely contains profanity, choose another username >:(")
        if password != confirmation: 
            return render_template("error.html", error="Password does not match retyped password!")

        try: cur.execute("INSERT INTO users (username, hash_password) VALUES (?, ?)", (username, generate_password_hash(password)))
        except sqlite3.IntegrityError: return render_template("error.html", error="Username already taken!")

        con.commit()
        return redirect("/login")
    return render_template("register.html")


@app.route("/whiteboard", methods=['GET', 'POST'])
@login_required
def whiteboard():
    username = cur.execute("SELECT username FROM users WHERE id = ?", 
                           (session["user_id"],)).fetchone()
    if request.method == 'POST':
        story = request.form.get("story")
        if profanity.contains_profanity(story): 
            return render_template("error.html", error="Story likely contains profanity, reword your story :P")
        if len(story) > 500:
            return render_template("error.html", error="Story exceeds 500 characters!")
        
        url = generateImage(story)
        if "https://i.ibb.co/" not in url: 
            return render_template("error.html", error="Sorry! Something is wrong! Try to change up the words!")

        cur.execute("INSERT INTO images (user_id, url, description, date) VALUES (?, ?, ?, ?)",
                    (session["user_id"], url, story, currenttime()))
        
        con.commit()
        return render_template("whiteboard.html", image=url, user=username[0])
    return render_template("whiteboard.html", user=username[0])


if __name__ == '__main__':
    app.run(debug=True)