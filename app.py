from flask import Flask, redirect, render_template, request, session, jsonify

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