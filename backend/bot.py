# bot.py
import ccxt
import time
from datetime import datetime
from threading import Event
from database import db  # Import db from database.py

from models.trade import Trade
from flask import current_app
from sqlalchemy.orm import sessionmaker

# Initialize exchange connections
exchange1 = ccxt.binance()
exchange2 = ccxt.kucoin()  # Replace with your choice of exchange

def fetch_price(exchange, symbol="BTC/USDT"):
    """Fetch the current price of the symbol from the specified exchange."""
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        print(f"Error fetching price from {exchange.id}: {e}")
        return None

def detect_arbitrage_opportunities():
    """Check for arbitrage opportunities between two exchanges."""
    price1 = fetch_price(exchange1)
    price2 = fetch_price(exchange2)

    if price1 is None or price2 is None:
        return None

    profit = abs(price1 - price2)
    profit_percentage = (profit / min(price1, price2)) * 100

    opportunity = {
        "timestamp": datetime.now().isoformat(),
        "exchange_buy": exchange1.id if price1 < price2 else exchange2.id,
        "exchange_sell": exchange1.id if price1 > price2 else exchange2.id,
        "currency": "BTC/USDT",
        "buy_price": min(price1, price2),
        "sell_price": max(price1, price2),
        "profit": round(profit, 2),
        "profit_percentage": round(profit_percentage, 4)
    }

    if profit_percentage > 0.0:  # Adjust threshold as needed
        return opportunity
    else:
        return None

def log_trade(opportunity, app):
    """Log the trade to the database."""
    with app.app_context():
        try:
            trade = Trade(
                timestamp=datetime.utcnow(),
                asset=opportunity['currency'],
                buy_exchange=opportunity['exchange_buy'],
                sell_exchange=opportunity['exchange_sell'],
                buy_price=opportunity['buy_price'],
                sell_price=opportunity['sell_price'],
                profit=opportunity['profit'],
                profit_percentage=opportunity['profit_percentage']
            )
            db.session.add(trade)
            db.session.commit()
            print("Trade logged successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error logging trade: {e}")




def run_bot(opportunities_list, stop_event, app):
    """Run the bot continuously to detect arbitrage opportunities."""
    print("Bot started...")
    while not stop_event.is_set():
        opportunity = detect_arbitrage_opportunities()
        if opportunity:
            print(f"Arbitrage Opportunity Detected: {opportunity}")
            opportunities_list.append(opportunity)
            log_trade(opportunity, app)  # Pass app to log_trade
        else:
            print("No arbitrage opportunity found.")
        time.sleep(10)  # Adjust the sleep duration as needed
    print("Bot stopped.")


