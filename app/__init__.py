from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
  app = Flask(__name__)
  
  app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost:5433/stock_advisor'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  db.init_app(app)
  migrate.init_app(app, db)

  from .routes import bp as routes_bp
  app.register_blueprint(routes_bp)

  with app.app_context():
    db.create_all()

  #Apple
  #Sentiment Summary: (From May 14 / Current Value(16:05): 188,90)
  #Positive: 41
  #Negative: 16
  #Neutral: 36

  #Intel
  #Sentiment Summary: (From May 14 / Current Value(16:10): 19,40)
  #Positive: 4
  #Negative: 4
  #Neutral: 4


  return app