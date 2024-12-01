from flask import Flask, redirect, render_template, request, session

from qotd import qotd
from location import fetch_therapy_data

app = Flask(__name__)
q = qotd()

@app.route("/")
def home():
    q = qotd()
    return render_template("index.html", qu=q)

@app.route("/video")
def video():
    return render_template("video.html")

@app.route("/help")
def help():
    return render_template("help.html")

@app.route('/therapy', methods=['GET', 'POST'])
def therapy():
    if request.method == 'GET':
        return render_template('index.html') 
    else:
        location = request.form.get("location")
        if not location: return "stop html hacking ur not him"

        data = fetch_therapy_data(location)
        if not data: return "we were unabel to find location. perhaps you typed it wrong?"
        
        return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)