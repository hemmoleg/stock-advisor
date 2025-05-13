from flask import Blueprint, jsonify, request
from .ai import analyze_sentiment

bp = Blueprint('routes', __name__)

@bp.route('/analyze', methods=['POST'])
def analyze():
  data = request.get_json()
  text = data.get('text')
  result = analyze_sentiment(text)
  return jsonify(result)