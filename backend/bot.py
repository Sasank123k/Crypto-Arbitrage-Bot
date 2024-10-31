# bot.py
import ccxt
import time
import pandas as pd
from datetime import datetime
from threading import Event
from database import db  # Import db from database.py

from models.trade import Trade
from flask import current_app
from sqlalchemy.orm import sessionmaker

# Initialize exchange connections
exchanges = {
    'binance': ccxt.binance(),
    'kucoin': ccxt.kucoin(),
    'kraken': ccxt.kraken(),
    'bitfinex': ccxt.bitfinex(),
    'coinbase': ccxt.coinbase(),
}

# Define the symbols you are interested in
symbols = ['BTC/USDT', 'ETH/USDT', 'LTC/USDT']  # Add more symbols if needed

# Define symbol mapping per exchange
symbol_mapping = {
    'binance': {
        'BTC/USDT': 'BTC/USDT',
        'ETH/USDT': 'ETH/USDT',
        'LTC/USDT': 'LTC/USDT',
    },
    'kucoin': {
        'BTC/USDT': 'BTC/USDT',
        'ETH/USDT': 'ETH/USDT',
        'LTC/USDT': 'LTC/USDT',
    },
    'kraken': {
        'BTC/USDT': 'BTC/USD',
        'ETH/USDT': 'ETH/USD',
        'LTC/USDT': 'LTC/USD',
    },
    'bitfinex': {
        'BTC/USDT': 'BTC/USD',
        'ETH/USDT': 'ETH/USD',
        'LTC/USDT': 'LTC/USD',
    },
    'coinbase': {
        'BTC/USDT': 'BTC/USD',
        'ETH/USDT': 'ETH/USD',
        'LTC/USDT': 'LTC/USD',
    },
}

# Optionally, set rate limit or API keys if necessary
for exchange in exchanges.values():
    exchange.enableRateLimit = True  # Enable rate limit to avoid being banned

cryptocurrencies = ['BTC/USDT', 'ETH/USDT', 'LTC/USDT']  # Include at least 3 cryptocurrencies

def fetch_price(exchange, symbol):
    """Fetch the current price of a symbol from an exchange."""
    # Load markets if not already loaded
    if not exchange.markets:
        exchange.load_markets()
    if symbol not in exchange.symbols:
        raise ValueError(f"{symbol} not available on {exchange.id}")
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']

def detect_arbitrage_opportunities():
    """Check for arbitrage opportunities among all exchanges and cryptocurrencies."""
    opportunities = []
    # Get a unique set of all symbols across exchanges
    all_symbols = set()
    for symbols_list in symbol_mapping.values():
        all_symbols.update(symbols_list.keys())

    for symbol in all_symbols:
        prices = {}
        # Fetch prices from all exchanges that support the symbol
        for exchange_name, exchange in exchanges.items():
            # Adjust symbol per exchange using symbol_mapping
            adjusted_symbol = symbol_mapping.get(exchange_name, {}).get(symbol)
            if adjusted_symbol is None:
                continue
            try:
                price = fetch_price(exchange, adjusted_symbol)
                prices[exchange_name] = price
            except Exception as e:
                print(f"Error fetching {adjusted_symbol} from {exchange_name}: {e}")
                continue

        # Compare prices across exchanges
        for buy_exchange in prices:
            for sell_exchange in prices:
                if buy_exchange != sell_exchange:
                    buy_price = prices[buy_exchange]
                    sell_price = prices[sell_exchange]
                    if buy_price < sell_price:
                        profit = sell_price - buy_price
                        profit_percentage = (profit / buy_price) * 100
                        opportunity = {
                            "timestamp": datetime.utcnow().isoformat(),
                            "exchange_buy": buy_exchange,
                            "exchange_sell": sell_exchange,
                            "currency": symbol,
                            "buy_price": round(buy_price, 2),
                            "sell_price": round(sell_price, 2),
                            "profit": round(profit, 2),
                            "profit_percentage": round(profit_percentage, 4),
                        }
                        opportunities.append(opportunity)
    return opportunities

def fetch_historical_data(exchange, symbol="BTC/USDT", timeframe="1d", since=None):
    """Fetch historical OHLCV data for backtesting."""
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def backtest(symbol="BTC/USDT", start_date="2023-01-01", end_date="2023-03-01"):
    start_timestamp = int(pd.Timestamp(start_date).timestamp() * 1000)
    end_timestamp = int(pd.Timestamp(end_date).timestamp() * 1000)

    # Fetch historical data from all exchanges that support the symbol
    exchange_data = {}
    for exchange_name, exchange in exchanges.items():
        try:
            # Adjust symbol per exchange using symbol_mapping
            adjusted_symbol = symbol_mapping.get(exchange_name, {}).get(symbol)
            if adjusted_symbol is None:
                print(f"{symbol} not mapped for {exchange_name}")
                continue

            if not exchange.markets:
                exchange.load_markets()
            if adjusted_symbol not in exchange.symbols:
                print(f"{adjusted_symbol} not available on {exchange_name}")
                continue
            data = fetch_historical_data(exchange, adjusted_symbol, "1d", since=start_timestamp)
            data = data[data['timestamp'] <= pd.to_datetime(end_date)]
            exchange_data[exchange_name] = data
        except Exception as e:
            print(f"Error fetching data from {exchange_name}: {e}")
            continue

    # Ensure we have at least two exchanges to compare
    if len(exchange_data) < 2:
        raise ValueError("Not enough exchanges support the selected symbol for backtesting.")

    # Merge dataframes on timestamp
    merged_data = None
    for exchange_name, data in exchange_data.items():
        data = data[['timestamp', 'close']]
        data = data.rename(columns={'close': f'close_{exchange_name}'})
        if merged_data is None:
            merged_data = data
        else:
            merged_data = pd.merge(merged_data, data, on='timestamp', how='inner')

    if merged_data is None or merged_data.empty:
        raise ValueError("No overlapping data available for backtesting.")

    total_profit = 0
    trades = []

    for i, row in merged_data.iterrows():
        # Find the exchange with the lowest price (buy) and the highest price (sell)
        prices = {col.replace('close_', ''): row[col] for col in merged_data.columns if 'close_' in col}
        buy_exchange = min(prices, key=prices.get)
        sell_exchange = max(prices, key=prices.get)
        buy_price = prices[buy_exchange]
        sell_price = prices[sell_exchange]

        if buy_exchange != sell_exchange and buy_price < sell_price:
            profit = sell_price - buy_price
            profit_percentage = (profit / buy_price) * 100
            trades.append({
                "timestamp": row['timestamp'].isoformat(),
                "buy_exchange": buy_exchange,
                "sell_exchange": sell_exchange,
                "buy_price": round(buy_price, 2),
                "sell_price": round(sell_price, 2),
                "profit": round(profit, 2),
                "profit_percentage": round(profit_percentage, 4),
            })
            total_profit += profit

    return {"total_profit": total_profit, "trades": trades}

def log_trade(opportunity, app):
    """Log the trade to the database."""
    with app.app_context():
        try:
            # Only log profitable trades
            if opportunity['profit'] > 0:
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

def run_bot(stop_event, app):
    """Run the bot continuously to detect arbitrage opportunities."""
    print("Bot started...")
    while not stop_event.is_set():
        opportunities = detect_arbitrage_opportunities()
        for opportunity in opportunities:
            # Log each opportunity as a trade
            log_trade(opportunity, app)
        time.sleep(10)  # Adjust the sleep duration as needed
    print("Bot stopped.")
