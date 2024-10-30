# models/trade.py
from database import db  # Import db from database.py
from datetime import datetime

class Trade(db.Model):
    __tablename__ = 'trades'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    asset = db.Column(db.String(20))
    buy_exchange = db.Column(db.String(50))
    sell_exchange = db.Column(db.String(50))
    buy_price = db.Column(db.Float)
    sell_price = db.Column(db.Float)
    profit = db.Column(db.Float)
    profit_percentage = db.Column(db.Float)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'asset': self.asset,
            'buy_exchange': self.buy_exchange,
            'sell_exchange': self.sell_exchange,
            'buy_price': self.buy_price,
            'sell_price': self.sell_price,
            'profit': self.profit,
            'profit_percentage': self.profit_percentage,
        }
