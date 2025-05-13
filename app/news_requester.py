import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NEWS_API_KEY")

api_key = "YOUR_API_KEY"
url = (
    "https://newsapi.org/v2/everything?"
    "q=stock OR market OR earnings&"
    "language=en&"
    "sortBy=publishedAt&"
    f"apiKey={api_key}"
)

response = requests.get(url)
articles = response.json()["articles"]

# Grab headlines
headlines = [article["title"] for article in articles]