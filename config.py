import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    FLASK_HOST = os.getenv('FLASK_HOST', 'localhost')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5433/stock_advisor')
    
    # API Keys
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    GPT_API_KEY = os.getenv('GPT_API_KEY')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')  # Allow external connections in production

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 