from datetime import datetime, time as dt_time, timedelta
from zoneinfo import ZoneInfo
from flask import Blueprint, jsonify, request, Response, stream_with_context
import json

#from app.claude_test import get_news_content_with_claude
from app.news_requester import get_closing_price_at_date, get_company_name_by_symbol, get_price_now, get_news_FINNHUB
from app.storage.storage import get_all_predictions_with_future_prices, prediction_for_company_and_date_exists, save_prediction, save_closing_price
from app.utils import save_future_closing_prices
from .ai import classify_text

bp = Blueprint('routes', __name__)

@bp.route('/analyze', methods=['POST'])
def analyze():
  data = request.get_json()
  text = data.get('text')
  result = classify_text(text)
  return jsonify(result)


@bp.route('/predictions', methods=['GET'])
def get_predictions():
    result = get_all_predictions_with_future_prices()
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

        # Send initial total count
        yield f"data: {json.dumps({'status': 'progress', 'total_news': total_news_count, 'classified_news': 0})}\n\n"

        for i, article in enumerate(news, 1):
            analysis = classify_text(article['summary'])
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

        base_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        # Save current stock price
        save_closing_price(symbol, base_date, stock_value)

        # Save future closing prices
        save_future_closing_prices(symbol, base_date)

        save_prediction(symbol, date_time, positive_count, negative_count, neutral_count, positive_probability, 
                        negative_probability, neutral_probability, stock_value)
        
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