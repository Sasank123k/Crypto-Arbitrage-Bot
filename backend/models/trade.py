# models/trade.py

from database import db

class Trade(db.Model):
    __tablename__ = 'trades'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    asset = db.Column(db.String(50), nullable=False)
    buy_exchange = db.Column(db.String(50), nullable=False)
    sell_exchange = db.Column(db.String(50), nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    sell_price = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    gross_profit = db.Column(db.Float, nullable=False)  # New Field
    profit = db.Column(db.Float, nullable=False)          # Net Profit
    profit_percentage = db.Column(db.Float, nullable=False)
    buy_fee = db.Column(db.Float, nullable=False)
    sell_fee = db.Column(db.Float, nullable=False)
    withdrawal_fee = db.Column(db.Float, nullable=False)
    buy_slippage = db.Column(db.Float, nullable=False)
    sell_slippage = db.Column(db.Float, nullable=False)
    latency = db.Column(db.Float, nullable=False)
    estimated_price_change = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "asset": self.asset,
            "buy_exchange": self.buy_exchange,
            "sell_exchange": self.sell_exchange,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            "amount": self.amount,
            "gross_profit": self.gross_profit,  # Include in dictionary
            "profit": self.profit,
            "profit_percentage": self.profit_percentage,
            "buy_fee": self.buy_fee,
            "sell_fee": self.sell_fee,
            "withdrawal_fee": self.withdrawal_fee,
            "buy_slippage": self.buy_slippage,
            "sell_slippage": self.sell_slippage,
            "latency": self.latency,
            "estimated_price_change": self.estimated_price_change
        }
