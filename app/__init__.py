from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('flask_cors')
logger.level = logging.DEBUG

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
  app = Flask(__name__)
  
  # Load configuration
  if config_name is None:
    config_name = os.getenv('FLASK_ENV', 'development')
  
  from config import config
  app.config.from_object(config[config_name])
  
  # Database configuration
  app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'postgresql://user:password@localhost:5433/stock_advisor'
  )
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  
  # CORS configuration for frontend
  #frontend_url = "" #os.getenv('FRONTEND_URL', 'http://localhost:3000')
  CORS(app, resources={
    r"/*": {
      "origins": ["http://localhost:3000", "https://stock-advisor-frontend.onrender.com"],
      "methods": ["GET", "POST", "OPTIONS", "DELETE", "PUT"],
      "allow_headers": ["Content-Type"]
    }
  })

  # Add CORS logging middleware
  @app.after_request
  def after_request(response):
      logger.info(f'CORS Request: {request.method} {request.url}')
      logger.info(f'Origin: {request.headers.get("Origin")}')
      logger.info(f'CORS Headers: {dict(response.headers)}')
      return response
  
  db.init_app(app)
  migrate.init_app(app, db)

  from .routes import bp as routes_bp
  app.register_blueprint(routes_bp)

  with app.app_context():
    db.create_all()

  return app