from datetime import datetime, time as dt_time, timedelta
from zoneinfo import ZoneInfo
from flask import Blueprint, jsonify, request, Response, stream_with_context
import json

#from app.claude_test import get_news_content_with_claude
from app.news_requester import check_market_holiday, get_closing_price_at_date, get_company_name_by_symbol, get_price_now, get_news_FINNHUB
from app.storage.storage import (
    get_all_predictions, 
    get_all_symbols, 
    prediction_for_company_and_date_exists, 
    save_prediction, 
    save_closing_price,
    update_last_price_timestamp,
    get_last_price_update,
    get_prediction_with_details
)
from app.utils import save_future_closing_prices
from .ai import classify_text
from app import db
from app.storage.db_models import PredictionSummary, ClosingPrice

bp = Blueprint('routes', __name__)

@bp.route('/analyze', methods=['POST'])
def analyze():
  data = request.get_json()
  text = data.get('text')
  result = classify_text(text)
  return jsonify(result)


@bp.route('/predictions', methods=['GET'])
def get_predictions():
    result = get_all_predictions()
    return jsonify(result)


@bp.route('/predictions/<int:prediction_id>', methods=['GET'])
def get_prediction_details(prediction_id):
    """Get detailed information about a specific prediction including news articles"""
    prediction = get_prediction_with_details(prediction_id)
    if prediction is None:
        return jsonify({'error': 'Prediction not found'}), 404
    return jsonify(prediction)


@bp.route('/symbols', methods=['GET'])
def get_symbols():
    result = get_all_symbols()
    return jsonify(result)

@bp.route('/make_prediction', methods=['GET'])
def make_prediction():
    symbol = request.args.get('symbol')
    date_str = request.args.get('date')

    if not symbol:
        return jsonify({'status': 'error', 'message': 'Symbol is required'}), 400

    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')

    def generate_updates():
        #check if prediction for date and company already exists
        if prediction_for_company_and_date_exists(symbol, date_str):
            print(f"Prediction for {symbol} on {date_str} already exists")
            yield f"data: {json.dumps({'status': 'error', 'message': f'Prediction for {symbol} on {date_str} already exists'})}\n\n"
            return

        news = get_news_FINNHUB(symbol, date_str)
        total_news_count = len(news)
        print(f"news for {symbol}: {total_news_count}")
        
        if total_news_count == 0:
            yield f"data: {json.dumps({'status': 'error', 'message': f'No news for {symbol}.'})}\n\n"
            return

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        positive_probability = 0
        negative_probability = 0
        neutral_probability = 0

        # Store classifications for later use
        classifications = []

        # Send initial total count
        yield f"data: {json.dumps({'status': 'progress', 'total_news': total_news_count, 'classified_news': 0})}\n\n"

        for i, article in enumerate(news, 1):
            analysis = classify_text(article['summary'])
            classifications.append(analysis)  # Store the classification
            print(f"Analysis ({i}/{total_news_count}): {analysis}")

            if analysis['sentiment'] == "Positive":
                positive_count += 1
            elif analysis['sentiment'] == "Negative":
                negative_count += 1
            elif analysis['sentiment'] == "Neutral":
                neutral_count += 1

            positive_probability += analysis['probabilities']['Positive']
            negative_probability += analysis['probabilities']['Negative']
            neutral_probability += analysis['probabilities']['Neutral']

            # Send progress update after each classification
            yield f"data: {json.dumps({'status': 'progress', 'total_news': total_news_count, 'classified_news': i})}\n\n"

        print(f"Sentiment Summary for {symbol}:")
        print(f"Positive: {positive_count} ({positive_probability})")
        print(f"Negative: {negative_count} ({negative_probability})")
        print(f"Neutral: {neutral_count} ({neutral_probability})")

        if date_str == datetime.now().strftime('%Y-%m-%d'):
            stock_value = get_price_now(symbol)
            date_time = datetime.combine(datetime.strptime(date_str, "%Y-%m-%d").date(), datetime.now(ZoneInfo("Europe/Berlin")).time())
        else:
            stock_value = get_closing_price_at_date(symbol, date_str)
            date_time = datetime.combine(datetime.strptime(date_str, "%Y-%m-%d").date(), dt_time(hour=23, minute=59, second=59))

        base_date: datetime.date = datetime.strptime(date_str, "%Y-%m-%d").date()

        # Save current stock price
        save_closing_price(symbol, base_date, stock_value)

        # Save future closing prices
        save_future_closing_prices(symbol, base_date)

        # Save prediction with news articles
        save_prediction(symbol, date_time, positive_count, negative_count, neutral_count, positive_probability, 
                        negative_probability, neutral_probability, stock_value, news_articles=news, classifications=classifications)
        
        final_result = {
            "status": "complete",
            "symbol": symbol,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "positive_probability": round(positive_probability, 2),
            "negative_probability": round(negative_probability, 2),
            "neutral_probability": round(neutral_probability, 2),
            "message": f"Prediction and sentiment summary for {symbol} on {datetime.strptime(date_str, '%Y-%m-%d').strftime('%d.%m.%Y')} saved successfully."
        }

        yield f"data: {json.dumps(final_result)}\n\n"

    return Response(
        stream_with_context(generate_updates()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'text/event-stream'
        }
    )


@bp.route('/check_prediction', methods=['GET'])
def check_prediction():
   symbol = request.args.get('symbol')


@bp.route('/set_closing_price', methods=['POST'])
def set_closing_price():
    data = request.get_json()
    symbol = data.get('symbol')
    date = data.get('date')

    if not symbol:
        return jsonify({"status": "error", 
                        "message": "Missing 'symbol' in request"}), 400

    if date is None:
        return jsonify({"status": "error", 
                        "message": "Missing 'date' in request"}), 400

    try:
      closing_price = get_closing_price_at_date(symbol, date)
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": f"Could not fetch closing price for {symbol} on {date}. {e}"
        }), 500

    # Save the closing price to the database
    save_closing_price(symbol, date, closing_price)

    return jsonify({
        "status": "success",
        "message": f"Closing price for {symbol} saved successfully.",
        "symbol": symbol,
        "date": date,
        "closing_price": closing_price
    }), 200

@bp.route('/update_closing_prices', methods=['POST'])
def update_closing_prices():
    # Get lookback days from request, default to 7 days
    data = request.get_json(silent=True) or {}
    lookback_days = data.get('lookback_days', 31)
    
    # Calculate the cutoff date
    cutoff_date = datetime.now().date() - timedelta(days=lookback_days)
    
    # Get all predictions since cutoff date
    predictions = PredictionSummary.query.filter(
        db.func.date(PredictionSummary.date_time) >= cutoff_date
    ).order_by(PredictionSummary.date_time.desc()).all()

    updates_summary = {
        'total_predictions_checked': 0,
        'prices_updated': 0,
        'weekend_dates_count': 0,
        'holiday_dates_count': 0,
        'symbols_updated': set(),
        'price_updates': [],  # List to store detailed update information
        'errors': []
    }

    future_days = [1, 2, 3, 7]
    
    for prediction in predictions:
        updates_summary['total_predictions_checked'] += 1
        base_date = prediction.date_time.date()
        
        for days_ahead in future_days:
            future_date = base_date + timedelta(days=days_ahead)
            
            # Skip if the future date is in the future (prices not available yet)
            if future_date >= datetime.now().date():
                continue
            
            # Check if it's a weekend
            if future_date.weekday() >= 5:
                updates_summary['weekend_dates_count'] += 1
                # Save the weekend information
                save_closing_price(prediction.symbol, future_date, None)
                continue
            
            # Check if it's a holiday
            if check_market_holiday(future_date):
                updates_summary['holiday_dates_count'] += 1
                # Save the holiday information
                save_closing_price(prediction.symbol, future_date, None)
                continue
                
            # Check if we already have this price
            existing_price = ClosingPrice.query.filter_by(
                symbol=prediction.symbol,
                date_time=future_date
            ).first()
            
            # If price doesn't exist or is None, try to fetch it
            if not existing_price or existing_price.closing_price is None:
                try:
                    closing_price = get_closing_price_at_date(prediction.symbol, future_date.strftime('%Y-%m-%d'))
                    if closing_price is not None:
                        save_closing_price(prediction.symbol, future_date, closing_price)
                        updates_summary['prices_updated'] += 1
                        updates_summary['symbols_updated'].add(prediction.symbol)
                        
                        # Add detailed update information
                        updates_summary['price_updates'].append({
                            'symbol': prediction.symbol,
                            'price_date': future_date.strftime('%Y-%m-%d'),
                            'closing_price': closing_price
                        })
                except Exception as e:
                    updates_summary['errors'].append(f"Error updating {prediction.symbol} for {future_date}: {str(e)}")

    # Convert set to list for JSON serialization
    updates_summary['symbols_updated'] = list(updates_summary['symbols_updated'])
    
    # Update the last price update timestamp if any prices were updated
    update_last_price_timestamp()
    
    return jsonify({
        'status': 'success',
        'summary': updates_summary
    })

@bp.route('/last_price_update', methods=['GET'])
def get_last_update():
    """Get the timestamp of the last price update"""
    print("Fetching last price update...")  # Debug log
    last_update = get_last_price_update()
    print(f"Last update: {last_update}")  # Debug log
    return jsonify({
        'last_update': last_update.isoformat() if last_update else None
    })