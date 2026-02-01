"""
Test Suite for VAYU Trading Bot
===============================
Unit tests for core components.
"""

import unittest
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.strategy.rsi_momentum import RSIMomentumStrategy, Signal
from src.strategy.risk_engine import RiskEngine, RiskLimits
from src.strategy.portfolio import PortfolioManager, PairConfig


class TestRSIStrategy(unittest.TestCase):
    """Test RSI momentum strategy."""
    
    def setUp(self):
        self.strategy = RSIMomentumStrategy(
            rsi_period=14,
            overbought=70,
            oversold=30
        )
    
    def test_signal_enum(self):
        """Test signal types exist."""
        self.assertEqual(Signal.HOLD.value, 0)
        self.assertEqual(Signal.LONG.value, 1)
        self.assertEqual(Signal.SHORT.value, -1)


class TestRiskEngine(unittest.TestCase):
    """Test risk management."""
    
    def setUp(self):
        self.limits = RiskLimits(
            max_position_size=1000.0,
            max_daily_loss=500.0,
            max_trades_per_day=10
        )
        self.engine = RiskEngine(self.limits)
    
    def test_position_size_limit(self):
        """Test position size enforcement."""
        size = self.engine.calculate_position_size(
            account_balance=10000,
            entry_price=50000,
            stop_price=49000
        )
        self.assertLessEqual(size * 50000, 1000.0)
    
    def test_circuit_breaker(self):
        """Test daily loss circuit breaker."""
        # Simulate daily P&L exceeding limit
        self.engine.daily_pnl = -600.0
        self.assertFalse(self.engine.can_trade())


class TestPortfolio(unittest.TestCase):
    """Test portfolio manager."""
    
    def setUp(self):
        pairs = [
            PairConfig("BTC/USD", risk_weight=1.5),
            PairConfig("ETH/USD", risk_weight=1.0),
            PairConfig("SOL/USD", risk_weight=0.8),
        ]
        self.portfolio = PortfolioManager(pairs)
    
    def test_pair_selection(self):
        """Test pair selection respects max limit."""
        selected = self.portfolio.select_pairs_for_trading(max_pairs=2)
        self.assertLessEqual(len(selected), 2)
    
    def test_position_sizing(self):
        """Test position sizes sum to total capital."""
        sizes = self.portfolio.get_position_sizes(total_capital=10000)
        total = sum(sizes.values())
        self.assertAlmostEqual(total, 10000.0, places=2)


class TestBacktestEngine(unittest.TestCase):
    """Test backtesting framework."""
    
    def test_import(self):
        """Test backtest engine can be imported."""
        try:
            from src.backtest.backtest_engine import BacktestEngine
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Import failed: {e}")


class TestPerformanceTracker(unittest.TestCase):
    """Test performance tracking."""
    
    def test_import(self):
        """Test performance tracker can be imported."""
        try:
            from src.utils.performance import PerformanceTracker
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Import failed: {e}")


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestRSIStrategy))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestPortfolio))
    suite.addTests(loader.loadTestsFromTestCase(TestBacktestEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceTracker))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
