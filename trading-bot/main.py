"""
VAYU Trading Bot - Main Engine
==============================
Orchestrates signal generation, risk management, and execution.
"""

import os
import sys
import time
import signal
from datetime import datetime
from typing import List, Dict

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.exchange.kraken_client import KrakenClient
from src.data.price_feed import PriceFeed
from src.strategy.rsi_momentum import RSIMomentumStrategy, Signal
from src.strategy.risk_engine import RiskEngine, RiskLimits
from src.execution.order_manager import OrderManager

class TradingBot:
    """
    Main trading bot orchestrator.
    """
    
    def __init__(
        self,
        symbols: List[str] = None,
        timeframe: str = "1h",
        sandbox: bool = True
    ):
        self.symbols = symbols or ["BTC/USD", "ETH/USD"]
        self.timeframe = timeframe
        self.sandbox = sandbox
        self.running = False
        
        # Initialize components
        print("🌀 Initializing VAYU Trading Bot...")
        
        self.client = KrakenClient(sandbox=sandbox)
        self.client.load_markets()
        print(f"✅ Connected to Kraken ({'sandbox' if sandbox else 'LIVE'})")
        
        self.feed = PriceFeed(self.client)
        self.strategy = RSIMomentumStrategy(timeframe=timeframe)
        self.risk = RiskEngine(RiskLimits())
        self.orders = OrderManager(self.client, self.risk)
        
        print(f"✅ Strategy: RSI Momentum on {timeframe}")
        print(f"✅ Trading pairs: {', '.join(self.symbols)}")
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\n🛑 Shutdown signal received...")
        self.running = False
    
    def check_signals(self):
        """
        Check for trading signals on all symbols.
        """
        for symbol in self.symbols:
            try:
                # Fetch price data
                df = self.feed.fetch_candles(symbol, self.timeframe, limit=250)
                
                if len(df) < 200:
                    print(f"⚠️ Insufficient data for {symbol}")
                    continue
                
                # Check for exit signals on open positions
                if symbol in self.orders.open_trades:
                    trade = self.orders.open_trades[symbol]
                    should_exit = self.strategy.check_exit(
                        df, trade.entry_price, 
                        Signal.LONG if trade.side == "buy" else Signal.SHORT
                    )
                    
                    if should_exit:
                        print(f"📤 Exit signal for {symbol}")
                        self.orders.exit_position(symbol)
                    continue
                
                # Check for entry signals
                result = self.strategy.generate_signal(df)
                
                if result.signal == Signal.LONG:
                    print(f"📈 LONG signal: {symbol} (RSI: {result.rsi:.1f}, Confidence: {result.confidence:.2f})")
                    self._enter_long(symbol, result)
                    
                elif result.signal == Signal.SHORT:
                    print(f"📉 SHORT signal: {symbol} (RSI: {result.rsi:.1f}, Confidence: {result.confidence:.2f})")
                    # Skip shorts for now (requires margin/futures)
                    print("   (Short signals ignored - spot trading only)")
                    
            except Exception as e:
                print(f"❌ Error checking {symbol}: {e}")
    
    def _enter_long(self, symbol: str, signal_result):
        """Execute long entry."""
        # Get current price and ATR for stop calculation
        df = self.feed.fetch_candles(symbol, self.timeframe, limit=50)
        current_price = df["close"].iloc[-1]
        atr = df["high"].rolling(14).max().iloc[-1] - df["low"].rolling(14).min().iloc[-1]
        atr = atr / 14 if atr > 0 else current_price * 0.02
        
        stop_price = current_price - (3 * atr)
        
        # Calculate position size
        # Assume $10,000 account for now (will fetch real balance later)
        account_balance = 10000
        confidence = signal_result.confidence
        
        size = self.risk.calculate_position_size(
            account_balance, current_price, stop_price, confidence
        )
        
        if size and size > 0:
            # Round to 6 decimal places for crypto
            size = round(size, 6)
            print(f"   Size: {size} @ ${current_price:,.2f}, Stop: ${stop_price:,.2f}")
            
            if not self.sandbox:
                self.orders.enter_position(symbol, "buy", size)
            else:
                print("   (Sandbox mode - order not executed)")
    
    def print_status(self):
        """Print current bot status."""
        print("\n" + "="*50)
        print(f"📊 VAYU Trading Bot Status")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Mode: {'SANDBOX' if self.sandbox else 'LIVE'}")
        
        risk_status = self.risk.get_status()
        print(f"   Daily P&L: ${risk_status['daily_pnl']:+.2f}")
        print(f"   Open Positions: {risk_status['open_positions']}")
        
        if risk_status['open_positions'] > 0:
            for symbol, trade in self.orders.open_trades.items():
                print(f"      - {symbol}: {trade.side} {trade.amount} @ ${trade.entry_price:,.2f}")
        
        print("="*50 + "\n")
    
    def run(self, check_interval: int = 300):
        """
        Main trading loop.
        
        Args:
            check_interval: Seconds between signal checks (default: 5 min)
        """
        self.running = True
        self.print_status()
        
        print(f"🚀 Bot running. Checking signals every {check_interval}s")
        print("   Press Ctrl+C to stop\n")
        
        last_check = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Check signals on interval
                if current_time - last_check >= check_interval:
                    print(f"\n🔍 Checking signals at {datetime.now().strftime('%H:%M:%S')}...")
                    self.check_signals()
                    self.print_status()
                    last_check = current_time
                
                # Small sleep to prevent CPU spinning
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Main loop error: {e}")
                time.sleep(5)
        
        # Shutdown
        print("\n🛑 Shutting down...")
        if self.orders.open_trades:
            print("   Closing open positions...")
            self.orders.emergency_close_all()
        print("✅ Bot stopped")


def main():
    """Entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="VAYU Trading Bot")
    parser.add_argument("--live", action="store_true", help="Enable live trading")
    parser.add_argument("--interval", type=int, default=300, help="Check interval in seconds")
    args = parser.parse_args()
    
    sandbox = not args.live
    
    if not sandbox:
        confirm = input("⚠️  LIVE TRADING MODE! Confirm? (yes/no): ")
        if confirm.lower() != "yes":
            print("Aborted.")
            return
    
    bot = TradingBot(sandbox=sandbox)
    bot.run(check_interval=args.interval)


if __name__ == "__main__":
    main()
