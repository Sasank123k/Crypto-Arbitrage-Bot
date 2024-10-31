# app.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from database import db  # Import db from database.py
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.trade import Trade

from threading import Thread, Event
import random
from bot import detect_arbitrage_opportunities, backtest, exchanges, symbol_mapping, fetch_price
import bot
import jwt
import datetime
app = Flask(__name__)
CORS(app)


app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crypto_arbitrage.db?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create the tables
with app.app_context():
    db.create_all()

# Backtest endpoint
@app.route('/api/backtest', methods=['POST'])
def backtest_bot():
    data = request.json
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    symbol = data.get("symbol", "BTC/USDT")

    if not start_date or not end_date or not symbol:
        return jsonify({"error": "Start date, end date, and symbol are required."}), 400

    try:
        result = backtest(symbol=symbol, start_date=start_date, end_date=end_date)
        return jsonify(result)
    except Exception as e:
        print(f"Error during backtest: {e}")
        return jsonify({"error": "Backtest failed."}), 500

# Trade history endpoint
@app.route('/api/trade-history', methods=['GET'])
def get_trade_history():
    try:
        trades = Trade.query.order_by(Trade.timestamp.desc()).all()
        trade_list = [trade.to_dict() for trade in trades]
        return jsonify(trade_list)
    except Exception as e:
        print(f"Error in get_trade_history: {e}")
        return jsonify({'error': 'Failed to retrieve trade history'}), 500

# Signup route
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 400

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

# Login route
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        # Generate a JWT token
        token = jwt.encode(
            {'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        
        # Return token along with the success message
        return jsonify({'message': 'Login successful', 'token': token}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401


# Bot control variables
bot_thread = None
is_bot_running = False
stop_event = Event()

# Endpoint to toggle bot
@app.route('/api/togglebot', methods=['POST'])
def toggle_bot():
    global bot_thread, is_bot_running, stop_event
    data = request.json
    isActive = data.get('isActive', False)
    if isActive and not is_bot_running:
        # Start the bot
        stop_event.clear()
        bot_thread = Thread(target=bot.run_bot, args=(stop_event, app))
        bot_thread.start()
        is_bot_running = True
        return jsonify({"isActive": True, "message": "Bot started"}), 200
    elif not isActive and is_bot_running:
        # Stop the bot
        stop_event.set()
        bot_thread.join()
        is_bot_running = False
        return jsonify({"isActive": False, "message": "Bot stopped"}), 200
    else:
        return jsonify({"isActive": is_bot_running}), 200

# Endpoint to get bot status
@app.route('/api/bot-status', methods=['GET'])
def get_bot_status():
    status = "active" if is_bot_running else "inactive"
    return jsonify({"status": status})

# Endpoint to get recent arbitrage opportunities
@app.route('/api/arbitrage-opportunities', methods=['GET'])
def get_arbitrage_opportunities():
    try:
        opportunities = detect_arbitrage_opportunities()
        return jsonify(opportunities)
    except Exception as e:
        print(f"Error fetching arbitrage opportunities: {e}")
        return jsonify({'error': 'Failed to fetch arbitrage opportunities'}), 500

# Endpoint for profit/loss summary
@app.route('/api/profit-loss-summary', methods=['GET'])
def get_profit_loss_summary():
    with app.app_context():
        try:
            total_profit = db.session.query(db.func.sum(Trade.profit)).scalar() or 0.0
            return jsonify({"total_profit": total_profit, "total_loss": 0.0})
        except Exception as e:
            print(f"Error fetching profit/loss summary: {e}")
            return jsonify({"error": "Failed to fetch profit/loss summary"}), 500

# Real-time market data endpoint (fetch live data)
@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    market_data = []
    try:
        # Fetch prices for each cryptocurrency from each exchange
        for exchange_name, exchange in exchanges.items():
            symbols = symbol_mapping.get(exchange_name, {})
            for standard_symbol, adjusted_symbol in symbols.items():
                try:
                    price = fetch_price(exchange, adjusted_symbol)
                    market_data.append({
                        "symbol": standard_symbol,
                        "exchange": exchange_name,
                        "price": round(price, 2)
                    })
                except Exception as e:
                    print(f"Error fetching {adjusted_symbol} from {exchange_name}: {e}")
                    continue

        return jsonify(market_data)
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return jsonify({"error": "Failed to fetch market data"}), 500

# User data endpoint
@app.route('/api/userdata', methods=['GET'])
def get_user_data():
    # Placeholder: Return user data
    return jsonify({"username": "User"})

# Update account endpoint
@app.route('/api/update-account', methods=['POST'])
def update_account():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Assuming you have user authentication in place
    # Replace 'current_user_id' with the actual user identification method
    current_user_id = data.get('user_id')  # This is just a placeholder
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.email = email
    if password:
        user.set_password(password)
    db.session.commit()
    return jsonify({'message': 'Account updated successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
