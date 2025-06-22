import requests

url = "https://newsapi.org/v2/everything"
params = {
    "q": "NVDA AND war",                 # Search query
    "apiKey": "3843c29a2c2147c896f3ac0284ca48cd",       # Replace with your API key
    "language": "en",
    "pageSize": 5
}

response = requests.get(url, params=params)

if response.status_code == 200:
    articles = response.json()["articles"]
    for article in articles:
        print(f"- {article['title']}\n  {article['url']}\n")
else:
    print("Error:", response.status_code)
