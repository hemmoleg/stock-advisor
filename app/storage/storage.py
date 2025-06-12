from app.news_requester import get_company_name_by_symbol
from app.storage.db_models import Company, PredictionSummary
from app import db

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


def save_prediction(symbol, date_time, positive_count, negative_count, neutral_count, positive_probability, 
                    negative_probability, neutral_probability, stock_value):
    
    if company_exists(symbol) is False:
        # If the company does not exist, create a new Company object
        name = get_company_name_by_symbol(symbol)
        new_company = Company(symbol=symbol, name=name)
        db.session.add(new_company)
        db.session.commit()
    
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