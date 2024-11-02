# test_bot.py

import unittest
from bot import BotManager
from unittest.mock import MagicMock

class TestBotManagerCalculations(unittest.TestCase):
    def setUp(self):
        # Mock Flask app context
        self.app = MagicMock()
        self.bot = BotManager(self.app)
    
    def test_calculate_net_profit(self):
        # Define test inputs
        buy_price = 100.0
        sell_price = 110.0
        amount = 1.0
        buy_fee = 0.01  # 1%
        sell_fee = 0.01  # 1%
        withdrawal_fee = 0.5
        buy_slippage = 0.005  # 0.5%
        sell_slippage = 0.005  # 0.5%
        estimated_change = 0.1  # $0.1
        
        # Expected Net Profit Calculation:
        # Total Buy Cost = (100 * 1) + (100 * 1 * 0.01) = 101
        # Total Sell Revenue = (110 * 1) - (110 * 1 * 0.01) = 108.9
        # Net Profit = 108.9 - 101 - 0.5 = 7.4
        # Adjust for slippage and price change:
        # Net Profit -= (100 * 1 * 0.005) + (110 * 1 * 0.005) + 0.1 = 0.5 + 0.55 + 0.1 = 1.15
        # Final Net Profit = 7.4 - 1.15 = 6.25
        
        expected_net_profit = 6.25
        
        # Perform calculation
        net_profit = self.bot.calculate_net_profit(
            buy_price=buy_price,
            sell_price=sell_price,
            amount=amount,
            buy_fee=buy_fee,
            sell_fee=sell_fee,
            withdrawal_fee=withdrawal_fee,
            buy_slippage=buy_slippage,
            sell_slippage=sell_slippage,
            estimated_change=estimated_change
        )
        
        self.assertAlmostEqual(net_profit, expected_net_profit, places=2)

if __name__ == '__main__':
    unittest.main()
