from sqlalchemy import Numeric
from app import db
from datetime import datetime, timezone

class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Company {self.symbol} - {self.name}>"


class LastPriceUpdate(db.Model):
    __tablename__ = 'last_price_update'

    id = db.Column(db.Integer, primary_key=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<LastPriceUpdate at {self.updated_at}>"


# Junction table for many-to-many relationship between predictions and news
prediction_news = db.Table('prediction_news',
    db.Column('prediction_id', db.Integer, db.ForeignKey('prediction_summaries.id', ondelete='CASCADE'), primary_key=True),
    db.Column('news_id', db.Integer, db.ForeignKey('classified_news.id', ondelete='CASCADE'), primary_key=True)
)


class PredictionSummary(db.Model):
    __tablename__ = 'prediction_summaries'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), db.ForeignKey('companies.symbol'), nullable=False, index=True)
    date_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    positive_count = db.Column(db.Integer, nullable=False)
    negative_count = db.Column(db.Integer, nullable=False)
    neutral_count = db.Column(db.Integer, nullable=False)
    
    positive_probability = db.Column(Numeric(5, 2), nullable=False)
    negative_probability = db.Column(Numeric(5, 2), nullable=False)
    neutral_probability = db.Column(Numeric(5, 2), nullable=False)
    
    stock_value = db.Column(db.Float, nullable=False)

    # Update the relationship configuration
    news_articles = db.relationship(
        'ClassifiedNews',
        secondary=prediction_news,
        backref=db.backref('prediction_summaries', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return f"<PredictionSummary {self.symbol} - {self.date_time}>"


class ClosingPrice(db.Model):
    __tablename__ = 'closing_prices'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), db.ForeignKey('companies.symbol'), nullable=False, index=True)
    date_time = db.Column(db.Date, nullable=False)
    closing_price = db.Column(db.Float, nullable=True)  # Allow NULL for weekend days
    is_weekend = db.Column(db.Boolean, nullable=False, default=False)  # Flag to mark weekend days
    is_holiday = db.Column(db.Boolean, nullable=False, default=False)  # Flag to mark holiday days
    
    # Add a unique constraint to ensure that the same symbol and date cannot be added multiple times
    __table_args__ = (
        db.UniqueConstraint('symbol', 'date_time', name='uq_symbol_date'),
    )


class ClassifiedNews(db.Model):
    __tablename__ = 'classified_news'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(1000), nullable=False, unique=True)  # Make URL unique
    date_time = db.Column(db.DateTime, nullable=False, index=True)
    classification = db.Column(db.String(20), nullable=False)  # 'Positive', 'Negative', or 'Neutral'
    confidence_score = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<ClassifiedNews {self.title[:30]}... - {self.classification}>"