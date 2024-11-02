# bot.py

import ccxt
import time
import pandas as pd
from datetime import datetime
from threading import Thread, Event
from database import db  # Import db from database.py
from models.trade import Trade
from models.config import Config  # Import Config model
import logging
import json
import os
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

        # Load fee configurations
        fees_path = os.path.join('config', 'fees.json')
        if not os.path.exists(fees_path):
            logging.error(f"Fees configuration file not found at {fees_path}.")
            self.exchange_fees = {}
        else:
            with open(fees_path) as f:
                self.exchange_fees = json.load(f)

        # Initialize exchange connections
        self.exchanges = {
            'binance': ccxt.binance(),
            'kucoin': ccxt.kucoin(),
            'kraken': ccxt.kraken(),
            'bitfinex': ccxt.bitfinex(),
            'coinbasepro': ccxt.coinbase(),  # Corrected to coinbasepro
        }

        # Define the symbols you are interested in
        self.symbols = ['BTC/USDT', 'ETH/USDT', 'LTC/USDT']  # Add more symbols if needed

        # Define symbol mapping per exchange
        self.symbol_mapping = {
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
            'coinbasepro': {
                'BTC/USDT': 'BTC/USD',
                'ETH/USDT': 'ETH/USD',
                'LTC/USDT': 'LTC/USD',
            },
        }

        # Define realistic factor ranges per currency
        self.realistic_factors = {
            'BTC/USDT': {
                'buy_slippage': (0.0005, 0.002),         # 0.05% to 0.2%
                'sell_slippage': (0.0005, 0.0025),       # 0.05% to 0.25%
                'latency': (0.3, 1.0),                    # 0.3 to 1.0 seconds
                'estimated_price_change': (100, 500),     # $100 to $500
            },
            'ETH/USDT': {
                'buy_slippage': (0.001, 0.003),          # 0.1% to 0.3%
                'sell_slippage': (0.001, 0.0035),        # 0.1% to 0.35%
                'latency': (0.4, 1.2),                    # 0.4 to 1.2 seconds
                'estimated_price_change': (20, 100),      # $20 to $100
            },
            'LTC/USDT': {
                'buy_slippage': (0.0015, 0.004),         # 0.15% to 0.4%
                'sell_slippage': (0.0015, 0.0045),       # 0.15% to 0.45%
                'latency': (0.5, 1.5),                    # 0.5 to 1.5 seconds
                'estimated_price_change': (10, 50),       # $10 to $50
            },
            # Add more symbols and their respective ranges as needed
        }

        # Enable rate limit to avoid being banned
        for exchange in self.exchanges.values():
            exchange.enableRateLimit = True

    def get_trading_fees(self, exchange_name, symbol):
        fees = self.exchange_fees.get(exchange_name, {}).get(symbol, {})
        return fees.get('maker_fee', 0.0), fees.get('taker_fee', 0.0)

    def get_withdrawal_fee(self, exchange_name, symbol):
        fees = self.exchange_fees.get(exchange_name, {}).get(symbol, {})
        return fees.get('withdrawal_fee', 0.0)

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

    def calculate_profits(self, buy_price, sell_price, amount, buy_fee, sell_fee, withdrawal_fee, buy_slippage, sell_slippage, estimated_change):
        """Calculate both gross and net profit."""
        # Gross Profit: Difference between sell and buy prices
        gross_profit = (sell_price - buy_price) * amount

        # Total cost to buy
        total_buy_cost = (buy_price * amount) + (buy_price * amount * buy_fee)

        # Total revenue from selling
        total_sell_revenue = (sell_price * amount) - (sell_price * amount * sell_fee)

        # Net profit before slippage and price change
        net_profit = total_sell_revenue - total_buy_cost - withdrawal_fee

        # Adjust for slippage
        net_profit -= (buy_price * amount * buy_slippage) + (sell_price * amount * sell_slippage)

        # Adjust for estimated price change due to latency
        net_profit -= estimated_change * amount

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
                            # Fetch fees
                            buy_fee_maker, buy_fee_taker = self.get_trading_fees(buy_exchange, symbol)
                            sell_fee_maker, sell_fee_taker = self.get_trading_fees(sell_exchange, symbol)
                            withdrawal_fee = self.get_withdrawal_fee(buy_exchange, symbol)
                            
                            # Assume taker fees are applicable
                            buy_fee = buy_fee_taker
                            sell_fee = sell_fee_taker

                            # Get realistic factor ranges for the currency
                            factors = self.realistic_factors.get(symbol, {})
                            buy_slippage = round(random.uniform(*factors.get('buy_slippage', (0.001, 0.002))), 4)
                            sell_slippage = round(random.uniform(*factors.get('sell_slippage', (0.001, 0.0025))), 4)
                            latency = round(random.uniform(*factors.get('latency', (0.5, 1.0))), 2)
                            estimated_price_change = round(random.uniform(*factors.get('estimated_price_change', (50, 150))), 2)

                            # Calculate profits
                            gross_profit, net_profit = self.calculate_profits(
                                buy_price=buy_price,
                                sell_price=sell_price,
                                amount=1.0,  # Configurable
                                buy_fee=buy_fee,
                                sell_fee=sell_fee,
                                withdrawal_fee=withdrawal_fee,
                                buy_slippage=buy_slippage,
                                sell_slippage=sell_slippage,
                                estimated_change=estimated_price_change
                            )

                            # Calculate profit percentage based on gross profit
                            profit_percentage = (gross_profit / buy_price) * 100 if buy_price != 0 else 0.0

                            opportunity = {
                                "timestamp": datetime.utcnow().isoformat(),
                                "exchange_buy": buy_exchange,
                                "exchange_sell": sell_exchange,
                                "currency": symbol,
                                "buy_price": round(buy_price, 2),
                                "sell_price": round(sell_price, 2),
                                "gross_profit": round(gross_profit, 2),  # New Field
                                "profit_percentage": round(profit_percentage, 4),
                                # Realistic Factors with Random Values
                                "buy_fee": round(buy_fee, 4),
                                "sell_fee": round(sell_fee, 4),
                                "withdrawal_fee": round(withdrawal_fee, 4),
                                "buy_slippage": buy_slippage,
                                "sell_slippage": sell_slippage,
                                "latency": latency,
                                "estimated_price_change": estimated_price_change,
                                "net_profit": round(net_profit, 2)  # New Field
                            }
                            opportunities.append(opportunity)
                            #logging.info(f"Detected Opportunity: {opportunity}")
        return opportunities

    def calculate_slippage(self, order_book, order_type, amount):
        """Calculate slippage percentage based on order book depth."""
        slippage = 0.0
        remaining_amount = amount

        if order_type == 'buy':
            asks = order_book['asks']
            best_price = asks[0][0]
            for price, qty in asks:
                if remaining_amount <= qty:
                    break
                else:
                    remaining_amount -= qty
                    slippage += (price - best_price) * qty
        elif order_type == 'sell':
            bids = order_book['bids']
            best_price = bids[0][0]
            for price, qty in bids:
                if remaining_amount <= qty:
                    break
                else:
                    remaining_amount -= qty
                    slippage += (best_price - price) * qty

        if amount > 0:
            slippage_percentage = slippage / (amount * best_price)
        else:
            slippage_percentage = 0.0

        return slippage_percentage

    def measure_latency(self, func, *args, **kwargs):
        """Measure the time taken to execute a function."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        latency = end_time - start_time
        return result, latency

    def estimate_price_change(self, exchange, symbol, latency):
        """Estimate price change during the latency period."""
        timeframe = '1m'  # 1-minute intervals
        limit = max(1, int(latency / 60) + 1)  # Number of minutes
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if not ohlcv or len(ohlcv) < 2:
                return 0.0
            # Calculate the average price change per minute
            price_changes = [ohlcv[i][4] - ohlcv[i-1][4] for i in range(1, len(ohlcv))]
            average_change = sum(price_changes) / len(price_changes) if price_changes else 0.0
            return average_change
        except Exception as e:
            logging.error(f"Error estimating price change for {symbol} on {exchange.id}: {e}")
            return 0.0

    def log_trade(self, opportunity, net_profit, details):
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
                    amount=details.get('amount', 1.0),  # Define the trade amount or make it configurable
                    gross_profit=opportunity['gross_profit'],  # New Field
                    profit=opportunity['net_profit'],          # Updated Field
                    profit_percentage=opportunity['profit_percentage'],
                    buy_fee=details.get('buy_fee', 0.0),
                    sell_fee=details.get('sell_fee', 0.0),
                    withdrawal_fee=details.get('withdrawal_fee', 0.0),
                    buy_slippage=details.get('buy_slippage', 0.0),
                    sell_slippage=details.get('sell_slippage', 0.0),
                    latency=details.get('latency', 0.0),
                    estimated_price_change=details.get('estimated_price_change', 0.0)
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
                    buy_exchange_name = opportunity['exchange_buy']
                    sell_exchange_name = opportunity['exchange_sell']
                    currency = opportunity['currency']
                    buy_price = opportunity['buy_price']
                    sell_price = opportunity['sell_price']
                    gross_profit = opportunity['gross_profit']
                    net_profit = opportunity['net_profit']
                    profit_percentage = opportunity['profit_percentage']

                    # Calculate loss percentage
                    loss_percentage = (-net_profit) / buy_price if buy_price != 0 else 0.0

                    # Enforce maximum loss limit (10%)
                    if net_profit < (-0.10 * buy_price):
                        logging.warning(f"Trade skipped: Loss exceeds 10%. Net Profit: {net_profit}")
                        continue  # Skip logging this trade

                    # Apply profit threshold
                    if net_profit >= (buy_price * profit_threshold):
                        # Log the trade
                        self.log_trade(opportunity, net_profit, {
                            'buy_fee': opportunity['buy_fee'],
                            'sell_fee': opportunity['sell_fee'],
                            'withdrawal_fee': opportunity['withdrawal_fee'],
                            'buy_slippage': opportunity['buy_slippage'],
                            'sell_slippage': opportunity['sell_slippage'],
                            'latency': opportunity['latency'],
                            'estimated_price_change': opportunity['estimated_price_change'],
                            'amount': 1.0  # Configurable
                        })
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
                # Get realistic factor ranges for the currency
                factors = self.realistic_factors.get(symbol, {})
                buy_slippage = round(random.uniform(*factors.get('buy_slippage', (0.001, 0.002))), 4)
                sell_slippage = round(random.uniform(*factors.get('sell_slippage', (0.001, 0.0025))), 4)
                latency = round(random.uniform(*factors.get('latency', (0.5, 1.0))), 2)
                estimated_price_change = round(random.uniform(*factors.get('estimated_price_change', (50, 150))), 2)

                # Fees (use fixed values or adjust as needed)
                buy_fee = 0.0010
                sell_fee = 0.0010
                withdrawal_fee = 0.0005

                # Calculate profits
                gross_profit, net_profit = self.calculate_profits(
                    buy_price=buy_price,
                    sell_price=sell_price,
                    amount=1.0,  # Configurable
                    buy_fee=buy_fee,
                    sell_fee=sell_fee,
                    withdrawal_fee=withdrawal_fee,
                    buy_slippage=buy_slippage,
                    sell_slippage=sell_slippage,
                    estimated_change=estimated_price_change
                )

                # Calculate profit percentage based on gross profit
                profit_percentage = (gross_profit / buy_price) * 100 if buy_price != 0 else 0.0

                # Calculate loss percentage
                loss_percentage = (-net_profit) / buy_price if buy_price != 0 else 0.0

                # Apply profit threshold and maximum loss limit
                if net_profit >= (buy_price * profit_threshold) and net_profit >= (-0.10 * buy_price):
                    trades.append({
                        "timestamp": row['timestamp'].isoformat(),
                        "buy_exchange": buy_exchange,
                        "sell_exchange": sell_exchange,
                        "currency": symbol,
                        "buy_price": round(buy_price, 2),
                        "sell_price": round(sell_price, 2),
                        "gross_profit": round(gross_profit, 2),  # New Field
                        "profit_percentage": round(profit_percentage, 4),
                        # Realistic Factors with Random Values
                        "buy_fee": buy_fee,  # Fixed or dynamic
                        "sell_fee": sell_fee,  # Fixed or dynamic
                        "withdrawal_fee": withdrawal_fee,  # Fixed or dynamic
                        "buy_slippage": buy_slippage,
                        "sell_slippage": sell_slippage,
                        "latency": latency,
                        "estimated_price_change": estimated_price_change,
                        "net_profit": round(net_profit, 2)  # New Field
                    })
                    total_profit += gross_profit  # Or net_profit based on preference
        return {"total_profit": total_profit, "trades": trades} 

