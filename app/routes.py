from datetime import datetime, time
from zoneinfo import ZoneInfo
from flask import Blueprint, jsonify, request

from app.news_requester import get_closing_price_at_date, get_company_name_by_symbol, get_price_now, get_news_FINNHUB, get_news_content_with_claude
from app.storage.storage import get_all_predictions, prediction_for_company_and_date_exists, save_prediction
from .ai import analyze_sentiment, classify_text

bp = Blueprint('routes', __name__)

@bp.route('/analyze', methods=['POST'])
def analyze():
  data = request.get_json()
  text = data.get('text')
  result = analyze_sentiment(text)
  return jsonify(result)


@bp.route('/predictions', methods=['GET'])
def get_predictions():
    result = get_all_predictions()
    return jsonify(result)


@bp.route('/test_claude', methods=['POST'])
def test_claude():
  #   "https://finnhub.io/api/news?id=3c78a7b5c32438c8a4189338d4dfdbbe36a4346c447b9f0c33ff4c0b5f41e716",
  #   "https://finnhub.io/api/news?id=03d1eb4e4810a67ea80e10e84d378acda25f46917af5d42e0b3486830e8a9b92",
  #   "https://finnhub.io/api/news?id=eb77fa2427125070dbf2e2b37cd576426637be3da38fc9bb13316f54233d5c01",


  #seeling alpha blocks get request
  #text = get_news_content_with_claude("https://finnhub.io/api/news?id=c77beeb0421258b17a45aac25cc409d62920cdf82d59900bff1053718e2422c1")
  
  #text = get_news_content_with_claude("https://www.computerbase.de/news/gaming/state-of-play-sony-kontert-switch-2-mit-massig-ankuendigungen-und-trailern.92991")

  text = get_news_content_with_claude("https://finnhub.io/api/news?id=3c78a7b5c32438c8a4189338d4dfdbbe36a4346c447b9f0c33ff4c0b5f41e716")

  return text, 200

@bp.route('/make_prediction', methods=['POST'])
def make_and_save_prediction():
  data = request.get_json()
  symbol = data.get('symbol')
  date = data.get('date')

  if not date:
    date = datetime.now().strftime('%Y-%m-%d')

  #check if prediction for date and company already exists
  if prediction_for_company_and_date_exists(symbol, date):
    return jsonify({
      "status": "error", 
      "message": f"Prediction for {symbol} on {date} already exists"
    }), 400

  news = get_news_FINNHUB(symbol, date)
  print(f"news for {symbol}: {len(news)}")
  
  if len(news) == 0:
    return jsonify({
      "status": "error", 
      "message": f"No news for {symbol}."
    }), 400

  positive_count = 0
  negative_count = 0
  neutral_count = 0

  positive_probability = 0
  negative_probability = 0
  neutral_probability = 0

  for article in news:
      #print(f"Headline: {article['headline']}\nSummary: {article['summary']}")
      #print(article['url'])
      analysis = classify_text(article['summary'])

      if analysis['sentiment'] == "Positive":
          positive_count += 1
      elif analysis['sentiment'] == "Negative":
          negative_count += 1
      elif analysis['sentiment'] == "Neutral":
          neutral_count += 1

      positive_probability += analysis['probabilities']['Positive']
      negative_probability += analysis['probabilities']['Negative']
      neutral_probability += analysis['probabilities']['Neutral']

  print(f"Sentiment Summary for {symbol}:")
  print(f"Positive: {positive_count} ({positive_probability})")
  print(f"Negative: {negative_count} ({negative_probability})")
  print(f"Neutral: {neutral_count} ({neutral_probability})")

  if date == datetime.now().strftime('%Y-%m-%d'):
    stock_value = get_price_now(symbol)
    date_time = datetime.combine(datetime.strptime(date, "%Y-%m-%d").date(), datetime.now(ZoneInfo("Europe/Berlin")).time())
  else:
    stock_value = get_closing_price_at_date(symbol, date)
    date_time = datetime.combine(datetime.strptime(date, "%Y-%m-%d").date(), time(hour=23, minute=59, second=59))

  save_prediction(symbol, date_time, positive_count, negative_count, neutral_count, positive_probability, 
                  negative_probability, neutral_probability, stock_value)
  
  result = {
      "symbol": symbol,
      "positive_count": positive_count,
      "negative_count": negative_count,
      "neutral_count": neutral_count,
      "positive_probability": positive_probability,
      "negative_probability": negative_probability,
      "neutral_probability": neutral_probability,
      "message": f"Prediction and sentiment summary for {symbol} saved successfully."
  }

  return jsonify(result), 200


@bp.route('/check_prediction', methods=['GET'])
def check_prediction():
   symbol = request.args.get('symbol')


@bp.route('/set_closing_price', methods=['POST'])
def set_closing_price():
    data = request.get_json()
    symbol = data.get('symbol')
    date = data.get('date')
    
    if date is None:
      date = datetime.today().strftime("%Y-%m-%d")
    
    dt = datetime.strptime(date, '%Y-%m-%d')
    from_unix = int(time.mktime(dt.timetuple()))
    to_unix = from_unix + 86400

    # Check if the closing price for the given symbol and date already exists
    # if prediction_for_company_and_date_exists(symbol, date):
    #     return jsonify({"status": "error", 
    #                     "message": f"Closing price for {symbol} already exists for {date}."
    #                     }), 400

    closing = get_closing_price_at_date(symbol, from_unix, to_unix)
    return closing, 200

    # Save the closing price to the database
    # save_closing_price(symbol, date_time, closing_price)

    return jsonify({"status": "success", 
                    "message": f"Closing price for {symbol} saved successfully."
                    }), 200