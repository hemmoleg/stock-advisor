from flask import Flask

from app.ai import analyze_title
from .news_requester import get_news_FINNHUB, get_news_NEWSAPI
import json

def create_app():
  app = Flask(__name__)
  from .routes import bp as routes_bp
  app.register_blueprint(routes_bp)

  #articles = get_yesterdays_news()

  # Save the headlines to a JSON file
  # with open("news_2025_05_12.json", "w") as f:
  #     json.dump(articles, f)

  # with open("news_2025_05_12.json", "r") as f:
  #   articles = json.load(f)

  # for art in articles[10:20]:
  #   title = art["title"]
  #   if title:
  #       print(analyze_title(title))
  #       print("\n\n")

  # Example usage
  news = get_news_FINNHUB("TSLA")

  for article in news[:5]:
      print(f"{article['headline']}\n{article['url']}\n")

  return app