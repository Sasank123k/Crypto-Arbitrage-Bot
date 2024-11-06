# ml_models/scripts/data_processing.py

import sys
import os

# Determine the absolute path to the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

# Add the project root to sys.path
if project_root not in sys.path:
    sys.path.append(project_root)



import pandas as pd
import numpy as np  # Import numpy to handle mathematical operations
from sqlalchemy import create_engine
from models.historical_data import HistoricalData
from database import db  # Ensure that database is initialized
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data(exchange='binance', symbol='BTC/USDT', timeframe='1d'):
    """
    Load historical data from the database.
    """
    query = HistoricalData.query.filter_by(
        exchange=exchange,
        symbol=symbol,
        timeframe=timeframe
    ).order_by(HistoricalData.timestamp.asc()).all()
    
    print(f"Fetched {len(query)} records from the database for {symbol} on {exchange} with timeframe {timeframe}")
    
    data = [{
        "timestamp": entry.timestamp,
        "open": entry.open,
        "high": entry.high,
        "low": entry.low,
        "close": entry.close,
        "volume": entry.volume
    } for entry in query]
    
    if data:
        print("Sample data loaded:", data[:5])
    else:
        print("No data found for the specified query.")

    df = pd.DataFrame(data)
    return df

def preprocess_data(df):
    """
    Preprocess the data for ML.
    """
    # Feature Engineering
    df['price_diff'] = df['close'] - df['open']
    df['log_price_diff'] = (df['price_diff'].abs() + 1).apply(lambda x: np.log(x))  # Use np.log instead of pd.np.log
    df['volatility'] = df['close'].rolling(window=5).std().fillna(0)

    # Labeling: 1 if next period's price_diff > 0, else 0
    df['future_price_diff'] = df['price_diff'].shift(-1)
    df['profitable_trade'] = (df['future_price_diff'] > 0).astype(int)

    # Drop rows with NaN values created by shifting
    df = df.dropna()

    # Select features and target
    features = ['price_diff', 'log_price_diff', 'volatility']
    target = 'profitable_trade'

    X = df[features]
    y = df[target]

    return X, y

def main():
    # Define which exchange and symbol to use for training
    exchange = 'binance'
    symbol = 'BTC/USDT'
    timeframe = '1d'

    # Load data from the database
    df = load_data(exchange=exchange, symbol=symbol, timeframe=timeframe)
    logger.info(f"Loaded {len(df)} records from the database.")

    # Preprocess data
    X, y = preprocess_data(df)
    logger.info(f"Preprocessed data: {X.shape[0]} samples with {X.shape[1]} features.")

    # Save processed data
    processed_data_dir = os.path.join(project_root, 'ml_models', 'data', 'processed')
    os.makedirs(processed_data_dir, exist_ok=True)
    X.to_csv(os.path.join(processed_data_dir, 'X_train.csv'), index=False)
    y.to_csv(os.path.join(processed_data_dir, 'y_train.csv'), index=False)
    logger.info("Data preprocessing completed and saved.")

if __name__ == "__main__":
    from app import app  # Ensure that your Flask app is importable
    with app.app_context():
        main()
