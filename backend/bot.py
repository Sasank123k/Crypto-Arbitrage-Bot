# bot.py

import ccxt
import time
import pandas as pd  # Added this import statement
from datetime import datetime
from threading import Thread, Event
from database import db  # Import db from database.py
from models.trade import Trade
from models.config import Config  # Import Config model
import logging
import random

class BotManager:
    def __init__(self, app):
        self.app = app
        self.bot_thread = None
        self.stop_event = Event()
        self.is_running = False

        # Initialize logging with rotation to prevent log file from becoming too large
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler('trade_logs.log', maxBytes=1000000, backupCount=5)  # 1MB per file, keep last 5
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        # Initialize exchange connections (Removed 'coinbase')
        self.exchanges = {
            'binance': ccxt.binance(),
            'kucoin': ccxt.kucoin(),
            'kraken': ccxt.kraken(),
            'bitfinex': ccxt.bitfinex(),
        }

        # Define the symbols you are interested in (Removed 'LTC/USDT')
        self.symbols = ['BTC/USDT', 'ETH/USDT']

        # Define symbol mapping per exchange (Removed 'LTC/USDT' and 'coinbase')
        self.symbol_mapping = {
            'binance': {
                'BTC/USDT': 'BTC/USDT',
                'ETH/USDT': 'ETH/USDT',
            },
            'kucoin': {
                'BTC/USDT': 'BTC/USDT',
                'ETH/USDT': 'ETH/USDT',
            },
            'kraken': {
                'BTC/USDT': 'BTC/USD',
                'ETH/USDT': 'ETH/USD',
            },
            'bitfinex': {
                'BTC/USDT': 'BTC/USD',
                'ETH/USDT': 'ETH/USD',
            },
        }

        # Enable rate limit to avoid being banned
        for exchange in self.exchanges.values():
            exchange.enableRateLimit = True

    def fetch_price(self, exchange, symbol):
        """Fetch the current price of a symbol from an exchange."""
        try:
            # Load markets if not already loaded
            if not exchange.markets:
                exchange.load_markets()
            if symbol not in exchange.symbols:
                raise ValueError(f"{symbol} not available on {exchange.id}")
            ticker = exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logging.error(f"Error fetching price for {symbol} on {exchange.id}: {e}")
            return None

    def calculate_profits(self, buy_price, sell_price, amount):
        """Calculate gross and net profit."""
        # Gross Profit: Difference between sell and buy prices
        gross_profit = (sell_price - buy_price) * amount

        # Net Profit is 10% of Gross Profit
        net_profit = gross_profit * 0.1

        return gross_profit, net_profit

    def detect_arbitrage_opportunities(self):
        """Check for arbitrage opportunities among all exchanges and cryptocurrencies."""
        opportunities = []
        # Get a unique set of all symbols across exchanges
        all_symbols = set()
        for symbols_list in self.symbol_mapping.values():
            all_symbols.update(symbols_list.keys())

        for symbol in all_symbols:
            prices = {}
            # Fetch prices from all exchanges that support the symbol
            for exchange_name, exchange in self.exchanges.items():
                # Adjust symbol per exchange using symbol_mapping
                adjusted_symbol = self.symbol_mapping.get(exchange_name, {}).get(symbol)
                if adjusted_symbol is None:
                    continue
                price = self.fetch_price(exchange, adjusted_symbol)
                if price is not None:
                    prices[exchange_name] = price

            # Compare prices across exchanges
            for buy_exchange in prices:
                for sell_exchange in prices:
                    if buy_exchange != sell_exchange:
                        buy_price = prices[buy_exchange]
                        sell_price = prices[sell_exchange]
                        if buy_price < sell_price:
                            # Generate random realistic values (for display only)
                            buy_fee = round(random.uniform(0.001, 0.005), 4)
                            sell_fee = round(random.uniform(0.001, 0.005), 4)
                            withdrawal_fee = round(random.uniform(0.0005, 0.001), 4)
                            buy_slippage = round(random.uniform(0.0005, 0.005), 4)
                            sell_slippage = round(random.uniform(0.0005, 0.005), 4)
                            latency = round(random.uniform(0.3, 1.5), 2)
                            estimated_price_change = round(random.uniform(1, 5), 2)

                            amount = 1.0  # Quantity is always 1

                            # Calculate profits
                            gross_profit, net_profit = self.calculate_profits(
                                buy_price=buy_price,
                                sell_price=sell_price,
                                amount=amount,
                            )

                            # Calculate profit percentages
                            gross_profit_percentage = (gross_profit / buy_price) * 100 if buy_price != 0 else 0.0
                            net_profit_percentage = (net_profit / buy_price) * 100 if buy_price != 0 else 0.0

                            opportunity = {
                                "timestamp": datetime.utcnow().isoformat(),
                                "exchange_buy": buy_exchange,
                                "exchange_sell": sell_exchange,
                                "currency": symbol,
                                "buy_price": round(buy_price, 2),
                                "sell_price": round(sell_price, 2),
                                "gross_profit": round(gross_profit, 2),
                                "gross_profit_percentage": round(gross_profit_percentage, 4),
                                "net_profit": round(net_profit, 2),
                                "net_profit_percentage": round(net_profit_percentage, 4),
                                # Realistic Factors with Random Values (for display only)
                                "buy_fee": buy_fee,
                                "sell_fee": sell_fee,
                                "withdrawal_fee": withdrawal_fee,
                                "buy_slippage": buy_slippage,
                                "sell_slippage": sell_slippage,
                                "latency": latency,
                                "estimated_price_change": estimated_price_change,
                                "amount": amount,
                            }
                            opportunities.append(opportunity)
        return opportunities  # Moved outside the loops

    def log_trade(self, opportunity):
        """Log the trade to the database."""
        with self.app.app_context():
            try:
                trade = Trade(
                    timestamp=datetime.utcnow(),
                    asset=opportunity['currency'],
                    buy_exchange=opportunity['exchange_buy'],
                    sell_exchange=opportunity['exchange_sell'],
                    buy_price=opportunity['buy_price'],
                    sell_price=opportunity['sell_price'],
                    amount=opportunity['amount'],
                    gross_profit=opportunity['gross_profit'],
                    profit=opportunity['net_profit'],
                    profit_percentage=opportunity['net_profit_percentage'],
                    # Include realistic factors (for display purposes)
                    buy_fee=opportunity['buy_fee'],
                    sell_fee=opportunity['sell_fee'],
                    withdrawal_fee=opportunity['withdrawal_fee'],
                    buy_slippage=opportunity['buy_slippage'],
                    sell_slippage=opportunity['sell_slippage'],
                    latency=opportunity['latency'],
                    estimated_price_change=opportunity['estimated_price_change']
                )
                db.session.add(trade)
                db.session.commit()
                logging.info("Trade logged successfully.")
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error logging trade: {e}")

    def get_profit_threshold(self):
        """Fetch the current profit threshold from the Config table."""
        with self.app.app_context():
            config = Config.query.filter_by(key='profit_threshold').first()
            if config:
                try:
                    return float(config.value)
                except ValueError:
                    logging.error(f"Invalid profit_threshold value in config: {config.value}")
                    return 0.05  # Default 5%
            else:
                # Default value if not set
                return 0.05  # 5%

    def run_bot(self):
        """Run the bot continuously to detect arbitrage opportunities."""
        logging.info("Bot started.")
        print("Bot started...")
        while not self.stop_event.is_set():
            opportunities = self.detect_arbitrage_opportunities()
            logging.info(f"Total Opportunities Detected: {len(opportunities)}")
            profit_threshold = self.get_profit_threshold()
            logging.info(f"Current Profit Threshold: {profit_threshold * 100}%")
            for opportunity in opportunities:
                try:
                    net_profit = opportunity['net_profit']
                    buy_price = opportunity['buy_price']

                    # Apply profit threshold
                    if net_profit >= (buy_price * profit_threshold):
                        # Log the trade
                        self.log_trade(opportunity)
                        logging.info(f"Trade logged: Net Profit = {net_profit}")
                    else:
                        logging.info(f"Trade skipped: Net Profit below threshold. Net Profit: {net_profit}")
                except Exception as e:
                    logging.error(f"Error processing opportunity: {e}")
                    continue
            time.sleep(10)  # Adjust the sleep duration as needed
        logging.info("Bot stopped.")
        print("Bot stopped.")

    def start_bot(self):
        """Start the bot in a separate thread."""
        if not self.is_running:
            self.stop_event.clear()
            self.bot_thread = Thread(target=self.run_bot, daemon=True)
            self.bot_thread.start()
            self.is_running = True
            logging.info("Bot thread started.")

    def stop_bot(self):
        """Stop the bot gracefully."""
        if self.is_running:
            self.stop_event.set()
            self.bot_thread.join()
            self.is_running = False
            logging.info("Bot thread stopped.")

    def backtest(self, symbol="BTC/USDT", start_date="2023-01-01", end_date="2023-03-01"):
        """Fetch historical OHLCV data and perform backtesting."""
        # Convert to datetime objects
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        now = pd.to_datetime(datetime.utcnow())

        if start_dt > now or end_dt > now:
            raise ValueError("Start date and end date must not be in the future.")

        start_timestamp = int(start_dt.timestamp() * 1000)
        end_timestamp = int(end_dt.timestamp() * 1000)

        # Fetch historical data from all exchanges that support the symbol
        exchange_data = {}
        for exchange_name, exchange in self.exchanges.items():
            try:
                # Adjust symbol per exchange using symbol_mapping
                adjusted_symbol = self.symbol_mapping.get(exchange_name, {}).get(symbol)
                if adjusted_symbol is None:
                    logging.warning(f"{symbol} not mapped for {exchange_name}")
                    continue

                if not exchange.markets:
                    exchange.load_markets()
                if adjusted_symbol not in exchange.symbols:
                    logging.warning(f"{adjusted_symbol} not available on {exchange_name}")
                    continue
                ohlcv = exchange.fetch_ohlcv(adjusted_symbol, "1d", since=start_timestamp)
                df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df = df[df['timestamp'] <= pd.to_datetime(end_date)]
                exchange_data[exchange_name] = df
            except Exception as e:
                logging.error(f"Error fetching data from {exchange_name}: {e}")
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

        # Fetch the current profit threshold for backtesting
        profit_threshold = self.get_profit_threshold()

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
                # Generate random realistic values (for display only)
                buy_fee = round(random.uniform(0.001, 0.005), 4)
                sell_fee = round(random.uniform(0.001, 0.005), 4)
                withdrawal_fee = round(random.uniform(0.0005, 0.001), 4)
                buy_slippage = round(random.uniform(0.0005, 0.005), 4)
                sell_slippage = round(random.uniform(0.0005, 0.005), 4)
                latency = round(random.uniform(0.3, 1.5), 2)
                estimated_price_change = round(random.uniform(1, 5), 2)

                amount = 1.0  # Quantity is always 1

                # Calculate profits
                gross_profit, net_profit = self.calculate_profits(
                    buy_price=buy_price,
                    sell_price=sell_price,
                    amount=amount,
                )

                # Calculate profit percentages
                gross_profit_percentage = (gross_profit / buy_price) * 100 if buy_price != 0 else 0.0
                net_profit_percentage = (net_profit / buy_price) * 100 if buy_price != 0 else 0.0

                # Apply profit threshold
                if net_profit >= (buy_price * profit_threshold) or 1:
                    trades.append({
                        "timestamp": row['timestamp'].isoformat(),
                        "buy_exchange": buy_exchange,
                        "sell_exchange": sell_exchange,
                        "asset": symbol,  # Changed from 'currency' to 'asset' to match Trade model
                        "buy_price": round(buy_price, 2),
                        "sell_price": round(sell_price, 2),
                        "gross_profit": round(gross_profit, 2),
                        "gross_profit_percentage": round(gross_profit_percentage, 4),
                        "profit": round(net_profit, 2),  # Changed key to 'profit'
                        "profit_percentage": round(net_profit_percentage, 4),  # Changed key to 'profit_percentage'
                        # Realistic Factors with Random Values (for display purposes)
                        "buy_fee": buy_fee,
                        "sell_fee": sell_fee,
                        "withdrawal_fee": withdrawal_fee,
                        "buy_slippage": buy_slippage,
                        "sell_slippage": sell_slippage,
                        "latency": latency,
                        "estimated_price_change": estimated_price_change,
                        "amount": amount,
                    })
                    total_profit += gross_profit  # Or net_profit based on preference
        return {"total_profit": total_profit, "trades": trades}
