from app.news_requester import get_company_name_by_symbol, check_market_holiday
from app.storage.db_models import Company, PredictionSummary, ClosingPrice, LastPriceUpdate
from app import db
from datetime import timedelta, datetime

def update_last_price_timestamp():
    """Update the timestamp of the last price update"""
    last_update = LastPriceUpdate.query.first()
    if last_update:
        last_update.updated_at = datetime.now()
    else:
        last_update = LastPriceUpdate(updated_at=datetime.now())
        db.session.add(last_update)
    db.session.commit()

def get_last_price_update():
    """Get the timestamp of the last price update"""
    last_update = LastPriceUpdate.query.first()
    return last_update.updated_at if last_update else None

def get_all_predictions():
    predictions = db.session.query(PredictionSummary, Company).join(Company, PredictionSummary.symbol == Company.symbol).all()
    
    result = [
        {
            "id": p.PredictionSummary.id,
            "symbol": p.PredictionSummary.symbol,
            "name": p.Company.name,
            "date_time": p.PredictionSummary.date_time.isoformat(),
            "positive_count": p.PredictionSummary.positive_count,
            "negative_count": p.PredictionSummary.negative_count,
            "neutral_count": p.PredictionSummary.neutral_count,
            "positive_probability": p.PredictionSummary.positive_probability,
            "negative_probability": p.PredictionSummary.negative_probability,
            "neutral_probability": p.PredictionSummary.neutral_probability,
            "stock_value": p.PredictionSummary.stock_value
        }
        for p in predictions
    ]
    
    return result


def get_all_predictions_with_future_prices():
    """Get all predictions with future closing prices for 1, 2, 3, and 7 days ahead"""
    predictions = db.session.query(PredictionSummary, Company).join(Company, PredictionSummary.symbol == Company.symbol).order_by(PredictionSummary.date_time.desc()).all()
    
    result = []
    future_days = [1, 2, 3, 7]
    
    for p in predictions:
        base_date = p.PredictionSummary.date_time.date()
        
        future_prices = {}
        for days_ahead in future_days:
            future_date = base_date + timedelta(days=days_ahead)
            
            # Query for closing price on this future date
            closing_price_entry = ClosingPrice.query.filter_by(
                symbol=p.PredictionSummary.symbol, 
                date_time=future_date
            ).first()
            
            price_info = {
                'price': None,
                'is_weekend': False,
                'is_holiday': False
            }
            
            if closing_price_entry is not None:
                price_info['price'] = closing_price_entry.closing_price
                price_info['is_weekend'] = closing_price_entry.is_weekend
                price_info['is_holiday'] = closing_price_entry.is_holiday
            
            future_prices[f"{days_ahead}_day"] = price_info
        
        # Create the enhanced prediction object
        prediction_with_prices = {
            "id": p.PredictionSummary.id,
            "symbol": p.PredictionSummary.symbol,
            "name": p.Company.name,
            "date_time": p.PredictionSummary.date_time.isoformat(),
            "positive_count": p.PredictionSummary.positive_count,
            "negative_count": p.PredictionSummary.negative_count,
            "neutral_count": p.PredictionSummary.neutral_count,
            "positive_probability": p.PredictionSummary.positive_probability,
            "negative_probability": p.PredictionSummary.negative_probability,
            "neutral_probability": p.PredictionSummary.neutral_probability,
            "stock_value": p.PredictionSummary.stock_value,
            "future_prices": future_prices
        }
        
        result.append(prediction_with_prices)
    
    return result


def get_all_symbols():
    symbols = db.session.query(Company.symbol).all()
    return [symbol[0] for symbol in symbols]

def save_prediction(symbol, date_time:str, positive_count, negative_count, neutral_count, positive_probability, 
                    negative_probability, neutral_probability, stock_value):
    
    if company_exists(symbol) is False:
        save_company(symbol)
    
    # Create a new SentimentSummary object
    prediction_summary = PredictionSummary(
        symbol=symbol,
        date_time=date_time,
        positive_count=positive_count,
        negative_count=negative_count,
        neutral_count=neutral_count,
        positive_probability=positive_probability,
        negative_probability=negative_probability,
        neutral_probability=neutral_probability,
        stock_value=stock_value
    )
    
    # Add the object to the session and commit it to the database
    db.session.add(prediction_summary)
    db.session.commit()


def prediction_for_company_and_date_exists(symbol, date):
    # Check if a prediction for the given symbol and date already exists Ignoring time
    existing_prediction = (PredictionSummary.query.filter_by(symbol=symbol)
                           .filter(db.func.date(PredictionSummary.date_time) == date).first())
    return existing_prediction is not None


def company_exists(symbol):
    # Query the Company table to check if the symbol exists
    existing_company = Company.query.filter_by(symbol=symbol).first()
    return existing_company is not None


def save_company(symbol):
    name = get_company_name_by_symbol(symbol)
    new_company = Company(symbol=symbol.upper(), name=name)
    db.session.add(new_company)
    db.session.commit()


def save_closing_price(symbol: str, date: datetime.date, closing_price):
    """Save a closing price to the database"""
    if company_exists(symbol) is False:
        name = get_company_name_by_symbol(symbol)
        new_company = Company(symbol=symbol, name=name)
        db.session.add(new_company)
        db.session.commit()
    
    # Check if the date is a weekend
    is_weekend = date.weekday() >= 5  # 5 = Saturday, 6 = Sunday
    
    # Check if the date is a holiday
    is_holiday = check_market_holiday(date)
    
    # Check if closing price already exists for this symbol and date
    existing_price = ClosingPrice.query.filter_by(symbol=symbol, date_time=date).first()
    if existing_price:
        # Update existing price
        existing_price.closing_price = None if (is_weekend or is_holiday) else closing_price
        existing_price.is_weekend = is_weekend
        existing_price.is_holiday = is_holiday
    else:
        # Create new closing price entry
        closing_price_entry = ClosingPrice(
            symbol=symbol,
            date_time=date,
            closing_price=None if (is_weekend or is_holiday) else closing_price,
            is_weekend=is_weekend,
            is_holiday=is_holiday
        )
        db.session.add(closing_price_entry)
    
    if is_weekend:
        print(f"Marked {symbol} on {date} as weekend day")
    elif is_holiday:
        print(f"Marked {symbol} on {date} as holiday")
    else:
        print(f"Saved closing price for {symbol} on {date}: {closing_price}")
    
    db.session.commit()