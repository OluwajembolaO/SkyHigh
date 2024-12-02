from openai import AzureOpenAI
import requests
import base64
from secret import *
from PIL import Image
from io import BytesIO
import json

IMGBB_API_KEY = IMGBB_API_KEY
AZURE_OPENAI_ENDPOINT = AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY = AZURE_OPENAI_API_KEY

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
    print(imageURL)
    return imageURL


userInput = input("How do you feel right now?:")
generateImage(userInput)