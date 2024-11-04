# verify_symbols.py

import ccxt
import logging
import sys

def setup_logging():
    """Configure logging to display INFO and ERROR messages."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def get_ccxt_version():
    """Retrieve the installed CCXT version."""
    return ccxt.__version__

def list_available_symbols(exchange_id, mapped_symbol):
    """
    Check if a specific symbol is available on the given exchange.

    Parameters:
    - exchange_id (str): The CCXT exchange identifier (e.g., 'kraken').
    - mapped_symbol (str): The symbol to check on the exchange (e.g., 'BTC/USD').

    Returns:
    - bool: True if the symbol is available, False otherwise.
    """
    try:
        exchange_class = getattr(ccxt, exchange_id)
    except AttributeError:
        logging.error(f"Exchange '{exchange_id}' is not recognized by CCXT.")
        return False

    exchange = exchange_class({
        'enableRateLimit': True,  # Respect rate limits
    })

    try:
        exchange.load_markets()
    except Exception as e:
        logging.error(f"Failed to load markets for {exchange_id}: {e}")
        return False

    if mapped_symbol in exchange.symbols:
        logging.info(f"  Symbol: {mapped_symbol} - AVAILABLE on {exchange_id.capitalize()}")
        return True
    else:
        logging.info(f"  Symbol: {mapped_symbol} - NOT AVAILABLE on {exchange_id.capitalize()}")
        return False

def main():
    setup_logging()

    # Display CCXT version
    ccxt_version = get_ccxt_version()
    logging.info(f"CCXT Version Installed: {ccxt_version}\n")

    # Define exchanges and symbol mappings
    symbol_mappings = {
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
    }

    # Iterate through each exchange and its symbols
    for exchange_id, symbols in symbol_mappings.items():
        logging.info(f"Checking symbols on {exchange_id.capitalize()}...")
        for standard_symbol, mapped_symbol in symbols.items():
            list_available_symbols(exchange_id, mapped_symbol)
        logging.info("")  # Add an empty line for readability

if __name__ == "__main__":
    main()
