import base64
from flask import redirect, session
from functools import wraps
from io import BytesIO
import json
from openai import AzureOpenAI
from PIL import Image
import requests
import sqlite3
import urllib.parse  # For URL encoding

from secret import *


def create_databases():
    con = sqlite3.connect("mental.db", check_same_thread=False)
    cur = con.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY NOT NULL,
            username TEXT NOT NULL,
            hash_password TEXT NOT NULL,
            UNIQUE (username)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS images (
            user_id INTEGER,
            id INTEGER PRIMARY KEY NOT NULL,
            images TEXT NOT NULL,
            date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY NOT NULL,
            date DATE DEFAULT CURRENT_DATE,
            quote TEXT NOT NULL,
            author TEXT NOT NULL
        )
    ''')

    con.commit()
    con.close()


def fetch_therapy_data(location):
    # Used for converting spaces commas and more shinanigans
    encoded_location = urllib.parse.quote(location)

    # Yelp API request URL with dynamic location
    url = f"https://api.yelp.com/v3/businesses/search?location={encoded_location}&categories=therapy,wellness&term=therapy&sort_by=best_match&limit=6"

    headers = {
        "accept": "application/json",
        "Authorization": YELP_GEOLOCATION_API_KEY
    }

    # Send the GET request to Yelp API
    response = requests.get(url, headers=headers)

    # Check if the response was successful
    if response.status_code == 200:
        data = response.json()  # Parse the JSON response

        # Prepare the structured data for the therapies dictionary
        therapies = {}

        # Loop through businesses and extract relevant info
        for i, business in enumerate(data.get('businesses', [])):
            therapy_name = business.get("name", "N/A")  # Create a unique name for each therapy place

            # Extract relevant details for each business
            therapy_info = {
                "location": business["location"].get("address1", "N/A"),
                "long": business["coordinates"].get("longitude", "N/A"),
                "lat": business["coordinates"].get("latitude", "N/A"),
                "PhoneNumber": business.get("phone", "N/A"),
                "rating": business.get("rating", "N/A"),
                "review_count": business.get("review_count", "N/A"),
                "url": business.get("url", "N/A"),
                "image_url": business.get("image_url", "N/A")
            }

            therapies[therapy_name] = therapy_info  # Add to the dictionary

        # Return the dictionary
        return therapies

    else:
        print(f"Failed to retrieve data. HTTP Status code: {response.status_code}")
        return None
    

theBot = AzureOpenAI(api_key=AZURE_OPENAI_API_KEY, azure_endpoint=AZURE_OPENAI_ENDPOINT, api_version="2024-05-01-preview")

def upload_image_to_imgbb(image_url, api_key):
    # Step 1: Download the image from the given URL
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image_data = response.content
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the image: {e}")
        return None

    # Step 2: Convert the image data to a base64 encoded string
    encoded_image = base64.b64encode(image_data).decode('utf-8')

    # Step 3: Upload the image to ImgBB
    upload_url = "https://api.imgbb.com/1/upload"
    payload = {
        'key': api_key,
        'image': encoded_image,
    }

    try:
        upload_response = requests.post(upload_url, data=payload)
        upload_response.raise_for_status()
        result = upload_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error uploading the image to ImgBB: {e}")
        return None

    # Step 4: Return the new URL of the uploaded image
    if result['status'] == 200:
        return result['data']['url']
    else:
        print(f"Error: {result['error']['message']}")
        return None
    
def generateImage(user_input):
    result = theBot.images.generate(
        model = "dalle3",
        prompt = user_input,
        n = 1,
    )
    
    imageURL = json.loads(result.model_dump_json())['data'][0]['url']
    responce = requests.get(imageURL)
    img = Image.open(BytesIO(responce.content))
    img.save('generated_image.jpg')
    return upload_image_to_imgbb(imageURL, IMGBB_API_KEY)


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def qotd():
    response = requests.get("https://zenquotes.io/api/today")
    if response.status_code == 200:
        data = response.json()
        s = f'"{data[0]["q"]}" — {data[0]["a"]}'
        return s
    else:
        return "Error occured"