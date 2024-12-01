import requests
import json
import urllib.parse  # For URL encoding
from secret import *

def fetch_therapy_data(location):

    # Used for converting spaces commas and more shinanigans
    encoded_location = urllib.parse.quote(location)

    # Yelp API request URL with dynamic location
    url = f"https://api.yelp.com/v3/businesses/search?location={encoded_location}&categories=therapy,wellness&term=therapy&sort_by=best_match&limit=5"

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

