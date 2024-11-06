# scripts/fetch_historical_data.py
import sys
import os

# Determine the absolute path to the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

# Add the project root to sys.path
if project_root not in sys.path:
    sys.path.append(project_root)
import ccxt
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.historical_data import HistoricalData
from database import db  # Ensure database is initialized
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_and_store_historical_data(exchange_id, symbol, timeframe, since, limit=1000):
    """
    Fetch historical OHLCV data from a specific exchange and store it in the database.
    """
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()
    exchange.enableRateLimit = True  # Respect rate limits

    all_ohlcv = []
    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
            if not ohlcv:
                break
            all_ohlcv.extend(ohlcv)
            logger.info(f"Fetched {len(ohlcv)} candles from {exchange_id} for {symbol} starting at {exchange.iso8601(ohlcv[-1][0])}")
            since = ohlcv[-1][0] + 1  # Increment since to fetch next batch
            time.sleep(exchange.rateLimit / 1000)  # Sleep to respect rate limit
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            break

    # Store data in the database
    with db.session.no_autoflush:
        for candle in all_ohlcv:
            timestamp = exchange.iso8601(candle[0])
            candle_datetime = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
            historical_entry = HistoricalData(
                exchange=exchange_id,
                symbol=symbol,
                timeframe=timeframe,
                timestamp=candle_datetime,
                open=candle[1],
                high=candle[2],
                low=candle[3],
                close=candle[4],
                volume=candle[5]
            )
            db.session.add(historical_entry)
        try:
            db.session.commit()
            logger.info(f"Stored {len(all_ohlcv)} candles in the database.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error storing data to database: {e}")

def main():
    # Define exchanges, symbols, and timeframes you want to fetch data for
    exchanges = ['binance', 'kraken', 'kucoin', 'bitfinex']  # Add or remove exchanges as needed
    symbols = ['BTC/USDT', 'ETH/USDT']  # Add or remove symbols as needed
    timeframe = '1d'  # Daily data; adjust as needed (e.g., '1h', '1m')

    # Define the time range for historical data
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=365)  # Fetch data for the past year

    since = int(start_time.timestamp() * 1000)  # CCXT uses milliseconds

    for exchange_id in exchanges:
        for symbol in symbols:
            logger.info(f"Fetching historical data for {symbol} from {exchange_id}")
            fetch_and_store_historical_data(exchange_id, symbol, timeframe, since)

if __name__ == "__main__":
    # Initialize Flask app context if necessary
    from app import app  # Ensure that your Flask app is importable
    with app.app_context():
        main()
