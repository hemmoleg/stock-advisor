from datetime import datetime, timedelta
from app.news_requester import get_closing_price_at_date
from app.storage.storage import save_closing_price


def get_date_ahead(date, days_ahead) -> str:
    """Calculate the date that many days ahead (including weekends)"""
    future_date = date + timedelta(days=days_ahead)
    return future_date.strftime('%Y-%m-%d')


def save_future_closing_prices(symbol, base_date: datetime.date):
    """Save closing prices for multiple future dates (1, 2, 3, and 7 days ahead)"""
    future_days = [1, 2, 3, 7]
    
    for days_ahead in future_days:
        future_date = get_date_ahead(base_date, days_ahead)
        try:
            price = get_closing_price_at_date(symbol, future_date)
            save_closing_price(symbol, future_date, price)
        except Exception as e:
            print(f"Could not save closing price for {symbol} on {future_date}: {e}") 