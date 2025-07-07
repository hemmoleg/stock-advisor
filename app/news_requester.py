from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv
import yfinance as yf

load_dotenv()
api_key = os.getenv("FINNHUB_API_KEY")

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

def get_news_FINNHUB(symbol: str, date: str):
    url = f"https://finnhub.io/api/v1/company-news"
    provided_date = datetime.strptime(date, "%Y-%m-%d")
    two_days_ago = (provided_date - timedelta(days=2)).strftime("%Y-%m-%d")
    
    # Format the provided date as the "to" date
    #to_date = date.strftime("%Y-%m-%d")

    print(f"Fetching news from: {two_days_ago}, to: {date}")

    params = {
        "symbol": symbol.upper(),        # stock symbol
        "from": two_days_ago,            # start date (YYYY-MM-DD)
        "to": date,                   # end date
        "token": api_key
    }
    response = requests.get(url, params=params)
    return response.json()

def get_price_now(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
    response = requests.get(url)
    data = response.json()
    return data.get("c")  # 'c' is the current price in Finnhub's API

def get_company_name_by_symbol(symbol):
    url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={api_key}"
    response = requests.get(url)
    data = response.json()
    return data.get("name") 

def get_closing_price_at_date(symbol: str, date_str: str):
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    next_day = date + timedelta(days=1)

    data = yf.download(symbol, start=date_str, end=next_day.strftime("%Y-%m-%d"), progress=False, auto_adjust=True)
  
    if data.empty:
        return None

    closing_price = float(round(data.loc[str(date)]['Close'][symbol],2))

    # If there's only one row, pandas may return a scalar, otherwise a Series
    if isinstance(closing_price, float):
        return closing_price
    else:
        return closing_price.iloc[0]

def check_market_holiday(date):
    """Check if a given date is a market holiday using Finnhub API"""
    url = f"https://finnhub.io/api/v1/stock/market-holiday?exchange=US&token={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        # Convert date to string format YYYY-MM-DD for comparison
        date_str = date.strftime('%Y-%m-%d')
        
        # Check if the date is in the holiday list
        # Only consider it a holiday if tradingHour is empty (full day holiday)
        for holiday in data.get('data', []):
            if holiday.get('atDate') == date_str and holiday.get('tradingHour') == '':
                return True
        
        return False
        
    except Exception as e:
        print(f"Error checking market holiday: {e}")
        return False  # Default to not a holiday in case of error