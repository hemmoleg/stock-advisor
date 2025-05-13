import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

def get_news_NEWSAPI():
  api_key = os.getenv("NEWS_API_KEY")
  url = (
      "https://newsapi.org/v2/everything?"
      "q=stock OR market OR earnings&"
      "language=en&"
      "from=2025-05-12&to=2025-05-12&sortBy=popularity&"
      f"apiKey={api_key}"
  )

  response = requests.get(url)
  articles = response.json()["articles"]

  # Grab headlines
  headlines = [article["title"] for article in articles]

  requests_remaining = response.headers.get("X-Cache-Remaining")

  print(response.headers)

  print(f"{requests_remaining} requests to newsapi remaining today.")

  return articles

def get_news_FINNHUB(symbol: str):
    api_key = os.getenv("FINNHUB_API_KEY")
    
    url = f"https://finnhub.io/api/v1/company-news"
    params = {
        "symbol": symbol.upper(),        # e.g. 'AAPL'
        "from": "2025-05-01",            # start date (YYYY-MM-DD)
        "to": "2025-05-13",              # end date
        "token": api_key
    }
    response = requests.get(url, params=params)
    return response.json()