import requests
from bs4 import BeautifulSoup

url = "https://gizmodo.com/google-pixel-buds-drop-to-practically-free-compared-to-apple-airpods-limited-stock-wont-wait-for-you-2000611450"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Print visible paragraphs
for p in soup.find_all("p"):
    print(p.get_text())
