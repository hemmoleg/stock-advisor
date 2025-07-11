from app.news_requester import get_company_name_by_symbol, check_market_holiday
from app.storage.db_models import Company, PredictionSummary, ClosingPrice, LastPriceUpdate, ClassifiedNews
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


def _build_prediction_response(prediction, include_news=False):
    """Helper function to build a consistent prediction response object
    
    Args:
        prediction: Tuple of (PredictionSummary, Company) from a joined query
        include_news: Whether to include news articles in the response
    """
    base_date = prediction.PredictionSummary.date_time.date()
    future_days = [1, 2, 3, 7]
    future_prices = {}
    
    for days_ahead in future_days:
        future_date = base_date + timedelta(days=days_ahead)
        
        # Query for closing price on this future date
        closing_price_entry = ClosingPrice.query.filter_by(
            symbol=prediction.PredictionSummary.symbol, 
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

    response = {
        "id": prediction.PredictionSummary.id,
        "symbol": prediction.PredictionSummary.symbol,
        "name": prediction.Company.name,
        "date_time": prediction.PredictionSummary.date_time.isoformat(),
        "positive_count": prediction.PredictionSummary.positive_count,
        "negative_count": prediction.PredictionSummary.negative_count,
        "neutral_count": prediction.PredictionSummary.neutral_count,
        "positive_probability": prediction.PredictionSummary.positive_probability,
        "negative_probability": prediction.PredictionSummary.negative_probability,
        "neutral_probability": prediction.PredictionSummary.neutral_probability,
        "stock_value": prediction.PredictionSummary.stock_value,
        "future_prices": future_prices
    }

    if include_news:
        # Get all news articles for this prediction using the relationship
        news_articles = prediction.PredictionSummary.news_articles.all()
        response["news_articles"] = [{
            "id": article.id,
            "title": article.title,
            "url": article.url,
            "date_time": article.date_time.isoformat(),
            "classification": article.classification,
            "confidence_score": article.confidence_score
        } for article in news_articles]

    return response


def get_all_predictions():
    """Get all predictions with future closing prices for 1, 2, 3, and 7 days ahead"""
    predictions = db.session.query(PredictionSummary, Company).join(
        Company, PredictionSummary.symbol == Company.symbol
    ).order_by(PredictionSummary.date_time.desc()).all()
    
    return [_build_prediction_response(p) for p in predictions]


def get_all_symbols():
    symbols = db.session.query(Company.symbol).all()
    return [symbol[0] for symbol in symbols]

def save_prediction(symbol, date_time:str, positive_count, negative_count, neutral_count, positive_probability, 
                    negative_probability, neutral_probability, stock_value, news_articles, classifications):
    
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

    # Process each news article
    for article, classification in zip(news_articles, classifications):
        # Try to find existing news article by URL
        news = ClassifiedNews.query.filter_by(url=article['url']).first()
        
        if not news:
            # Create new news article if it doesn't exist
            news = ClassifiedNews(
                title=article['headline'],
                url=article['url'],
                date_time=datetime.fromtimestamp(article['datetime']),
                classification=classification['sentiment'],
                confidence_score=classification['probabilities'][classification['sentiment']]
            )
            db.session.add(news)
        
        # Always associate the news article (whether new or existing) with the prediction
        prediction_summary.news_articles.append(news)
    
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


def get_prediction_with_details(prediction_id: int):
    """Get a detailed prediction including news articles and future prices"""
    prediction = db.session.query(PredictionSummary, Company).join(
        Company, PredictionSummary.symbol == Company.symbol
    ).filter(PredictionSummary.id == prediction_id).first()
    
    if not prediction:
        return None
    
    return _build_prediction_response(prediction, include_news=True)