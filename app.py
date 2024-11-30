from flask import Flask, redirect, render_template, request, session
from flask_session import Session

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/chat-box")
def home():
    return render_template("home.html")

@app.route("/quote-generator")
def home():
    return render_template("quote-gen.html")

@app.route("/help-center")
def home():
    return render_template("help.html")