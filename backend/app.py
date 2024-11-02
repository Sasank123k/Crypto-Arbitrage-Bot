# app.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate  # Import Flask-Migrate
from database import db  # Import db from database.py
from models.trade import Trade
from models.config import Config  # Import the Config model

from bot import BotManager
import datetime
import logging
from sqlalchemy import case  # Ensure this import is present

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key'  # Retain if planning to re-enable authentication later
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crypto_arbitrage.db?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize logging with rotation to prevent log file from becoming too large
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler('app_logs.log', maxBytes=1000000, backupCount=5)  # 1MB per file, keep last 5
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Initialize BotManager
bot_manager = BotManager(app)

# Create the tables (if not using migrations)
with app.app_context():
    db.create_all()

# Backtest endpoint (public access)

@app.route('/api/backtest', methods=['POST'])
def backtest_bot():
    data = request.json
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    symbol = data.get("symbol", "BTC/USDT")

    if not start_date or not end_date or not symbol:
        return jsonify({"error": "Start date, end date, and symbol are required."}), 400

    try:
        result = bot_manager.backtest(symbol=symbol, start_date=start_date, end_date=end_date)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error during backtest: {e}", exc_info=True)
        return jsonify({"error": "Backtest failed."}), 500

# Trade history endpoint (public access)
@app.route('/api/trade-history', methods=['GET'])
def get_trade_history():
    try:
        trades = Trade.query.order_by(Trade.timestamp.desc()).all()
        trade_list = [trade.to_dict() for trade in trades]
        return jsonify(trade_list)
    except Exception as e:
        logging.error(f"Error in get_trade_history: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve trade history'}), 500

# Endpoint to toggle bot (public access)
@app.route('/api/togglebot', methods=['POST'])
def toggle_bot():
    data = request.json
    isActive = data.get('isActive', False)
    if isActive and not bot_manager.is_running:
        # Start the bot
        bot_manager.start_bot()
        logging.info("Bot started.")
        return jsonify({"isActive": True, "message": "Bot started"}), 200
    elif not isActive and bot_manager.is_running:
        # Stop the bot
        bot_manager.stop_bot()
        logging.info("Bot stopped.")
        return jsonify({"isActive": False, "message": "Bot stopped"}), 200
    else:
        status = "running" if bot_manager.is_running else "stopped"
        return jsonify({"isActive": bot_manager.is_running, "message": f"Bot is already {status}."}), 200

# Endpoint to get bot status (public access)
@app.route('/api/bot-status', methods=['GET'])
def get_bot_status():
    status = "active" if bot_manager.is_running else "inactive"
    return jsonify({"status": status})

# Endpoint to get recent arbitrage opportunities (public access)
@app.route('/api/arbitrage-opportunities', methods=['GET'])
def get_arbitrage_opportunities():
    try:
        opportunities = bot_manager.detect_arbitrage_opportunities()
        return jsonify(opportunities)
    except Exception as e:
        logging.error(f"Error fetching arbitrage opportunities: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch arbitrage opportunities'}), 500

# Endpoint for profit/loss summary (public access)
@app.route('/api/profit-loss-summary', methods=['GET'])
def get_profit_loss_summary():
    with app.app_context():
        try:
            total_profit = db.session.query(db.func.sum(Trade.gross_profit)).scalar() or 0.0
            total_net_profit = db.session.query(db.func.sum(Trade.profit)).scalar() or 0.0
            total_loss = db.session.query(
                db.func.sum(
                    case(
                        (Trade.profit < 0, Trade.profit),
                        else_=0.0
                    )
                )
            ).scalar() or 0.0
            return jsonify({"total_gross_profit": round(total_profit, 2), 
                            "total_net_profit": round(total_net_profit, 2), 
                            "total_loss": round(total_loss, 2)})
        except Exception as e:
            logging.error(f"Error fetching profit/loss summary: {e}", exc_info=True)
            return jsonify({"error": "Failed to fetch profit/loss summary"}), 500

# Real-time market data endpoint (fetch live data) (public access)
@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    market_data = []
    try:
        # Fetch prices for each cryptocurrency from each exchange
        for exchange_name, exchange in bot_manager.exchanges.items():
            symbols = bot_manager.symbol_mapping.get(exchange_name, {})
            for standard_symbol, adjusted_symbol in symbols.items():
                try:
                    price = bot_manager.fetch_price(exchange, adjusted_symbol)
                    if price is not None:
                        market_data.append({
                            "symbol": standard_symbol,
                            "exchange": exchange_name,
                            "price": round(price, 2)
                        })
                except Exception as e:
                    logging.error(f"Error fetching {adjusted_symbol} from {exchange_name}: {e}", exc_info=True)
                    continue

        return jsonify(market_data)
    except Exception as e:
        logging.error(f"Error fetching market data: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch market data"}), 500

# Endpoint to get the current profit threshold
@app.route('/api/config/profit-threshold', methods=['GET'])
def get_profit_threshold():
    try:
        config = Config.query.filter_by(key='profit_threshold').first()
        if config:
            profit_threshold = float(config.value)
        else:
            # Default profit threshold (e.g., 5%)
            profit_threshold = 0.05
        return jsonify({"profit_threshold": profit_threshold}), 200
    except Exception as e:
        logging.error(f"Error fetching profit threshold: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch profit threshold"}), 500

# Endpoint to set the profit threshold
@app.route('/api/config/profit-threshold', methods=['POST'])
def set_profit_threshold():
    data = request.json
    profit_threshold = data.get('profit_threshold')

    if profit_threshold is None:
        return jsonify({"error": "profit_threshold is required."}), 400

    try:
        profit_threshold = float(profit_threshold)
        if not (0 < profit_threshold < 1):
            return jsonify({"error": "profit_threshold must be between 0 and 1."}), 400

        config = Config.query.filter_by(key='profit_threshold').first()
        if config:
            config.value = str(profit_threshold)
        else:
            config = Config(key='profit_threshold', value=str(profit_threshold))
            db.session.add(config)
        db.session.commit()
        logging.info(f"Profit threshold set to {profit_threshold * 100}%.")
        return jsonify({"profit_threshold": profit_threshold, "message": "Profit threshold updated."}), 200
    except ValueError:
        return jsonify({"error": "Invalid profit_threshold value. It must be a number between 0 and 1."}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error setting profit threshold: {e}", exc_info=True)
        return jsonify({"error": "Failed to set profit threshold"}), 500

# Placeholder for /api/userdata endpoint to prevent 404 errors
@app.route('/api/userdata', methods=['GET'])
def get_user_data():
    return jsonify({"message": "User data endpoint is disabled."}), 200

# Placeholder for /api/update-account endpoint to prevent 404 errors
@app.route('/api/update-account', methods=['POST'])
def update_account():
    return jsonify({'message': 'Account update endpoint is disabled.'}), 200

if __name__ == '__main__':
    app.run(debug=True)
