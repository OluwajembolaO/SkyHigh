from openai import AzureOpenAI
import requests
from secret import *
from PIL import Image
from io import BytesIO
import json


AZURE_OPENAI_ENDPOINT = AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY = AZURE_OPENAI_API_KEY

theBot = AzureOpenAI(api_key=AZURE_OPENAI_API_KEY, azure_endpoint=AZURE_OPENAI_ENDPOINT, api_version="2024-05-01-preview")

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
    return imageURL


userInput = input("How do you feel right now?:")
generateImage(userInput)