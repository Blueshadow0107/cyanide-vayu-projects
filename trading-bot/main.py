"""
VAYU Trading Bot - Main Engine
==============================
Orchestrates signal generation, risk management, and execution.
With paper trading simulation and reporting.
"""

import os
import sys
import time
import signal
from datetime import datetime
from typing import List, Dict, Optional

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.exchange.kraken_client import KrakenClient
from src.data.price_feed import PriceFeed
from src.strategy.rsi_momentum import RSIMomentumStrategy, Signal
from src.strategy.risk_engine import RiskEngine, RiskLimits
from src.execution.order_manager import OrderManager
from src.utils.paper_report import PaperTradingReport

class TradingBot:
    """
    Main trading bot orchestrator with paper trading support.
    """
    
    def __init__(
        self,
        symbols: List[str] = None,
        timeframe: str = "1h",
        sandbox: bool = True,
        paper_mode: bool = True
    ):
        self.symbols = symbols or ["BTC/USD", "ETH/USD"]
        self.timeframe = timeframe
        self.sandbox = sandbox
        self.paper_mode = paper_mode
        self.running = False
        
        # Paper trading state
        self.paper_balance = 10000.0  # Starting paper balance
        self.paper_positions: Dict[str, dict] = {}
        self.paper_trades_count = 0
        
        # Initialize components
        print("🌀 Initializing VAYU Trading Bot...")
        
        self.client = KrakenClient(sandbox=sandbox)
        self.client.load_markets()
        print(f"✅ Connected to Kraken ({'sandbox' if sandbox else 'LIVE'})")
        
        self.feed = PriceFeed(self.client)
        self.strategy = RSIMomentumStrategy(timeframe=timeframe, rsi_oversold=40, rsi_overbought=60)
        self.risk = RiskEngine(RiskLimits())
        self.orders = OrderManager(self.client, self.risk)
        self.paper_report = PaperTradingReport()
        
        print(f"✅ Strategy: RSI Momentum on {timeframe}")
        print(f"✅ Trading pairs: {', '.join(self.symbols)}")
        print(f"✅ Mode: {'PAPER TRADING' if paper_mode else 'LIVE EXECUTION'}")
        
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
                
                current_price = df["close"].iloc[-1]
                
                # Check for exit signals on open positions
                if symbol in self.paper_positions:
                    position = self.paper_positions[symbol]
                    should_exit = self.strategy.check_exit(
                        df, position["entry_price"], 
                        Signal.LONG if position["side"] == "buy" else Signal.SHORT
                    )
                    
                    if should_exit:
                        print(f"📤 Exit signal for {symbol}")
                        self._exit_paper_position(symbol, current_price, "RSI mean reversion")
                    continue
                
                # Check for entry signals
                result = self.strategy.generate_signal(df)
                
                if result.signal == Signal.LONG:
                    print(f"📈 LONG signal: {symbol} (RSI: {result.rsi:.1f}, Confidence: {result.confidence:.2f})")
                    self._enter_paper_long(symbol, result, current_price)
                    
                elif result.signal == Signal.SHORT:
                    print(f"📉 SHORT signal: {symbol} (RSI: {result.rsi:.1f}, Confidence: {result.confidence:.2f})")
                    # Skip shorts for now (requires margin/futures)
                    print("   (Short signals ignored - spot trading only)")
                    
            except Exception as e:
                print(f"❌ Error checking {symbol}: {e}")
    
    def _enter_paper_long(self, symbol: str, signal_result, current_price: float):
        """Execute paper long entry."""
        # Get ATR for stop calculation
        df = self.feed.fetch_candles(symbol, self.timeframe, limit=50)
        high = df["high"].rolling(14).max().iloc[-1]
        low = df["low"].rolling(14).min().iloc[-1]
        atr = (high - low) / 14 if high and low else current_price * 0.02
        
        stop_price = current_price - (3 * atr)
        
        # Calculate position size based on risk
        confidence = signal_result.confidence
        size = self.risk.calculate_position_size(
            self.paper_balance, current_price, stop_price, confidence
        )
        
        if size and size > 0:
            size = round(size, 6)
            position_value = size * current_price
            
            # Record paper trade
            trade_idx = self.paper_report.record_entry(symbol, "buy", current_price, size)
            
            self.paper_positions[symbol] = {
                "trade_index": trade_idx,
                "side": "buy",
                "amount": size,
                "entry_price": current_price,
                "stop_price": stop_price,
                "entry_time": datetime.now()
            }
            
            print(f"   📝 PAPER TRADE: {size} {symbol} @ ${current_price:,.2f}")
            print(f"   Stop: ${stop_price:,.2f}, Value: ${position_value:,.2f}")
    
    def _exit_paper_position(self, symbol: str, exit_price: float, reason: str):
        """Exit a paper position."""
        if symbol not in self.paper_positions:
            return
        
        position = self.paper_positions[symbol]
        
        # Calculate P&L
        if position["side"] == "buy":
            pnl = (exit_price - position["entry_price"]) * position["amount"]
        else:
            pnl = (position["entry_price"] - exit_price) * position["amount"]
        
        self.paper_balance += pnl
        
        # Record in report
        self.paper_report.record_exit(position["trade_index"], exit_price, reason)
        
        del self.paper_positions[symbol]
        self.paper_trades_count += 1
        
        emoji = "🟢" if pnl > 0 else "🔴"
        print(f"   {emoji} PAPER CLOSE: {symbol} P&L: ${pnl:+.2f} | Balance: ${self.paper_balance:,.2f}")
    
    def check_paper_stops(self):
        """Check stop losses on paper positions."""
        for symbol, position in list(self.paper_positions.items()):
            try:
                current_price = self.feed.get_latest_price(symbol)
                
                if position["side"] == "buy" and current_price <= position["stop_price"]:
                    print(f"🛑 Stop loss hit for {symbol}")
                    self._exit_paper_position(symbol, current_price, "Stop loss")
                    
            except Exception as e:
                print(f"❌ Error checking stops for {symbol}: {e}")
    
    def print_status(self):
        """Print current bot status."""
        print("\n" + "="*50)
        print(f"📊 VAYU Trading Bot Status")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Mode: {'PAPER' if self.paper_mode else 'LIVE'}")
        print(f"   Paper Balance: ${self.paper_balance:,.2f}")
        
        risk_status = self.risk.get_status()
        print(f"   Paper Positions: {len(self.paper_positions)}")
        
        if self.paper_positions:
            for symbol, pos in self.paper_positions.items():
                current = self.feed.get_latest_price(symbol)
                unrealized = (current - pos["entry_price"]) * pos["amount"]
                print(f"      - {symbol}: {pos['amount']} @ ${pos['entry_price']:,.2f} (Unrealized: ${unrealized:+.2f})")
        
        print("="*50 + "\n")
    
    def print_report(self):
        """Print paper trading report."""
        self.paper_report.print_report()
    
    def run(self, check_interval: int = 300):
        """
        Main trading loop.
        
        Args:
            check_interval: Seconds between signal checks (default: 5 min)
        """
        self.running = True
        self.print_status()
        
        print(f"🚀 Bot running. Checking signals every {check_interval}s")
        print("   Commands: Ctrl+C to stop, will auto-generate report on exit\n")
        
        last_check = 0
        last_report = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # Check stops more frequently
                if self.paper_positions:
                    self.check_paper_stops()
                
                # Check signals on interval
                if current_time - last_check >= check_interval:
                    print(f"\n🔍 Checking signals at {datetime.now().strftime('%H:%M:%S')}...")
                    self.check_signals()
                    self.print_status()
                    last_check = current_time
                
                # Print report every hour
                if current_time - last_report >= 3600:
                    print("\n" + "="*50)
                    print("📊 HOURLY REPORT")
                    print("="*50)
                    self.print_report()
                    last_report = current_time
                
                # Small sleep to prevent CPU spinning
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Main loop error: {e}")
                time.sleep(5)
        
        # Shutdown
        print("\n🛑 Shutting down...")
        
        # Close all paper positions
        if self.paper_positions:
            print("   Closing paper positions...")
            for symbol in list(self.paper_positions.keys()):
                current_price = self.feed.get_latest_price(symbol)
                self._exit_paper_position(symbol, current_price, "Bot shutdown")
        
        # Final report
        print("\n" + "="*50)
        print("📊 FINAL PAPER TRADING REPORT")
        print("="*50)
        self.print_report()
        
        print("\n✅ Bot stopped")


def main():
    """Entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="VAYU Trading Bot")
    parser.add_argument("--live", action="store_true", help="Enable live trading")
    parser.add_argument("--paper", action="store_true", help="Force paper mode (default)")
    parser.add_argument("--interval", type=int, default=300, help="Check interval in seconds")
    parser.add_argument("--report", action="store_true", help="Generate report from existing trades")
    args = parser.parse_args()
    
    if args.report:
        report = PaperTradingReport()
        report.print_report()
        return
    
    # Default to paper mode unless --live explicitly used
    paper_mode = not args.live
    sandbox = not args.live
    
    if args.live:
        confirm = input("⚠️  LIVE TRADING MODE! Confirm? (yes/no): ")
        if confirm.lower() != "yes":
            print("Aborted. Running in paper mode instead.")
            paper_mode = True
            sandbox = True
    
    bot = TradingBot(sandbox=sandbox, paper_mode=paper_mode)
    bot.run(check_interval=args.interval)


if __name__ == "__main__":
    main()
