from flask import Flask, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from qotd import qotd
from location import fetch_therapy_data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///database.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

q = qotd()

@app.route("/")
def home():
    q = qotd()
    return render_template("index.html", qu=q)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session['user_id'] = user.id
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid email or password")
    return render_template('login.html')

@app.route("/video")
def video():
    return render_template("video.html")

@app.route("/help")
def help():
    return render_template("help.html")

@app.route('/therapy', methods=['GET', 'POST'])
def therapy():
    if request.method == 'GET':
        return render_template('therapy.html') 
    else:
        location = request.form.get("location")
        if not location: return "stop html hacking ur not him"

        data = fetch_therapy_data(location)
        if not data: return "we were unabel to find location. perhaps you typed it wrong?"
        
        return render_template('therapy.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)