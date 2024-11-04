import ccxt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def test_fetch(exchange_id, symbol):
    try:
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class()
        exchange.load_markets()
        if symbol in exchange.symbols:
            ticker = exchange.fetch_ticker(symbol)
            price = ticker.get('last')
            logger.info(f"{exchange_id.capitalize()} - {symbol}: {price}")
        else:
            logger.error(f"{symbol} not available on {exchange_id}")
    except Exception as e:
        logger.error(f"Error fetching {symbol} on {exchange_id}: {e}")

# Test symbols
test_cases = [
    ('kraken', 'XXBTZUSD'),
    ('kraken', 'XETHZUSD'),
    ('bitfinex', 'tBTCUSD'),
    ('bitfinex', 'tETHUSD'),
    ('bitfinex', 'tDOGEUSD'),
    ('binance', 'BTC/USDT'),
    ('kucoin', 'BTC/USDT'),
]

for exchange_id, symbol in test_cases:
    test_fetch(exchange_id, symbol)
