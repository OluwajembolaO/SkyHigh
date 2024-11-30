from flask import Flask, redirect, render_template, request, session

from functions import qotd

app = Flask(__name__)
q = qotd()

@app.route("/")
def home():
    return render_template("home.html", qu = q)

@app.route("/chatbot")
def chat():
    return render_template("chat.html")

@app.route("/video")
def video():
    return render_template("video.html")

@app.route("/help")
def help():
    return render_template("help.html")

if __name__ == '__main__':
    app.run(debug=True)