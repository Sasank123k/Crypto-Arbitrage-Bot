from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from database import db  # Import db from database.py
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.trade import Trade

from threading import Thread, Event
import random
import bot  # Import your bot logic

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crypto_arbitrage.db?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create the tables
with app.app_context():
    db.create_all()





# trade history

# app.py

# app.py

@app.route('/api/trade-history', methods=['GET'])
def get_trade_history():
    try:
        trades = Trade.query.order_by(Trade.timestamp.desc()).all()
        trade_list = [trade.to_dict() for trade in trades]
        return jsonify(trade_list)
    except Exception as e:
        print(f"Error in get_trade_history: {e}")
        return jsonify({'error': 'Failed to retrieve trade history'}), 500

# ---------------- Existing Routes ---------------- #

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
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

# ---------------- Bot Control and New Routes ---------------- #

# Bot control variables
bot_thread = None
is_bot_running = False
stop_event = Event()
opportunities_list = []  # Shared list to store detected opportunities

# Endpoint to toggle bot
@app.route('/api/togglebot', methods=['POST'])
def toggle_bot():
    global bot_thread, is_bot_running, stop_event
    data = request.json
    isActive = data.get('isActive', False)
    if isActive and not is_bot_running:
        # Start the bot
        stop_event.clear()
        bot_thread = Thread(target=bot.run_bot, args=(opportunities_list, stop_event, app))
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
    # Return the last 10 opportunities
    recent_opportunities = opportunities_list[-10:]
    return jsonify(recent_opportunities)

# Endpoint for profit/loss summary
@app.route('/api/profit-loss-summary', methods=['GET'])
def get_profit_loss_summary():
    # Placeholder: Generate random profit/loss data
    # You can replace this with actual calculations
    summary = {
        "total_profit": random.randint(1000, 5000),
        "total_loss": random.randint(500, 1000),
    }
    return jsonify(summary)

# Real-time market data endpoint (fetch live data)
@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    market_data = {}
    try:
        # Fetch BTC price from Binance
        btc_price_binance = bot.fetch_price(bot.exchange1)
        market_data['BTC_Binance'] = {
            "price": round(btc_price_binance, 2),
            "exchange": bot.exchange1.name
        }

        # Fetch BTC price from Coinbase Pro
        btc_price_coinbase = bot.fetch_price(bot.exchange2)
        market_data['BTC_CoinbasePro'] = {
            "price": round(btc_price_coinbase, 2),
            "exchange": bot.exchange2.name
        }

        return jsonify(market_data)
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return jsonify({"error": "Failed to fetch market data"}), 500

# User data endpoint
@app.route('/api/userdata', methods=['GET'])
def get_user_data():
    # Placeholder: Return user data
    return jsonify({"username": "User"})

if __name__ == '__main__':
    app.run(debug=True)







#update account

@app.route('/api/update-account', methods=['POST'])
def update_account():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Assuming you have user authentication in place
    # Replace 'current_user_id' with the actual user identification method
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.email = email
    if password:
        user.set_password(password)
    db.session.commit()
    return jsonify({'message': 'Account updated successfully'}), 200

