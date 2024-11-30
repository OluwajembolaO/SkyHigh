import requests

def qotd():
    response = requests.get("https://zenquotes.io/api/today")
    if response.status_code == 200:
        data = response.json()
        s = f'"{data[0]["q"]}" — {data[0]["a"]}'
        return s
    else:
        return "Error occured"
