#!/usr/bin/env python3
"""
Kraken Trading Bot - MVP Implementation
Paper trading mode with RSI momentum strategy
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import os

class KrakenTradingBot:
    def __init__(self, api_key=None, private_key=None, paper_trading=True):
        """Initialize Kraken trading bot"""
        self.paper_trading = paper_trading
        
        # Initialize exchange
        config = {
            'apiKey': api_key,
            'secret': private_key,
            'enableRateLimit': True,
        }
        
        self.paper_trading = paper_trading
        if paper_trading:
            print("📝 PAPER TRADING MODE ENABLED (Simulated - no real orders)")
        
        self.exchange = ccxt.kraken(config)
        
        # Trading configuration
        self.risk_per_trade = 0.01  # 1% per trade
        self.max_daily_drawdown = 0.05  # 5% daily circuit breaker
        self.max_positions = 3
        self.rsi_period = 14
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        
        # Track state
        self.positions = []
        self.daily_pnl = 0
        self.starting_equity = None
        self.peak_equity = None
        self.today = datetime.now().date()
        
        # Trading pairs
        self.pairs = ['BTC/USD', 'ETH/USD']
        
    def get_balance(self):
        """Get account balance"""
        try:
            balance = self.exchange.fetch_balance()
            usd = balance.get('USD', {}).get('free', 0)
            btc = balance.get('BTC', {}).get('free', 0)
            eth = balance.get('ETH', {}).get('free', 0)
            
            total = usd  # Simplified - ignoring crypto value for now
            
            if self.starting_equity is None:
                self.starting_equity = total
                self.peak_equity = total
            
            return {
                'USD': usd,
                'BTC': btc,
                'ETH': eth,
                'total': total
            }
        except Exception as e:
            print(f"❌ Error fetching balance: {e}")
            return None
    
    def calculate_rsi(self, closes, period=14):
        """Calculate RSI for a series of closing prices"""
        deltas = np.diff(closes)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum()/period
        down = -seed[seed < 0].sum()/period
        rs = up/down if down != 0 else 0
        rsi = np.zeros_like(closes)
        rsi[:period] = 100. - 100./(1. + rs)
        
        for i in range(period, len(closes)):
            delta = deltas[i - 1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
            
            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            rs = up/down if down != 0 else 0
            rsi[i] = 100. - 100./(1. + rs)
        
        return rsi
    
    def fetch_ohlcv(self, symbol, timeframe='1h', limit=100):
        """Fetch OHLCV data"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"❌ Error fetching OHLCV for {symbol}: {e}")
            return None
    
    def get_signal(self, symbol):
        """Generate trading signal based on RSI"""
        df = self.fetch_ohlcv(symbol, timeframe='1h', limit=50)
        if df is None or len(df) < self.rsi_period:
            return None
        
        closes = df['close'].values
        rsi = self.calculate_rsi(closes, self.rsi_period)
        current_rsi = rsi[-1]
        
        # Get trend from 4h timeframe
        df_4h = self.fetch_ohlcv(symbol, timeframe='4h', limit=20)
        if df_4h is not None and len(df_4h) >= 2:
            trend = "up" if df_4h['close'].iloc[-1] > df_4h['close'].iloc[-5] else "down"
        else:
            trend = "neutral"
        
        signal = None
        strength = 0
        
        if current_rsi < self.rsi_oversold and trend == "up":
            signal = "BUY"
            strength = (self.rsi_oversold - current_rsi) / self.rsi_oversold
        elif current_rsi > self.rsi_overbought and trend == "down":
            signal = "SELL"
            strength = (current_rsi - self.rsi_overbought) / (100 - self.rsi_overbought)
        
        return {
            'symbol': symbol,
            'signal': signal,
            'rsi': current_rsi,
            'trend': trend,
            'strength': strength,
            'price': closes[-1]
        }
    
    def calculate_position_size(self, entry_price, stop_price, balance):
        """Calculate position size based on risk"""
        risk_amount = balance * self.risk_per_trade
        price_risk = abs(entry_price - stop_price)
        
        if price_risk == 0:
            return 0
        
        position_size = risk_amount / price_risk
        
        # Limit to 10% of account per position
        max_position_value = balance * 0.10
        max_size = max_position_value / entry_price
        
        return min(position_size, max_size)
    
    def check_circuit_breaker(self):
        """Check if we should halt trading"""
        balance = self.get_balance()
        if balance is None:
            return True  # Halt if we can't get balance
        
        current_equity = balance['total']
        
        # Update peak equity
        if self.peak_equity is None or current_equity > self.peak_equity:
            self.peak_equity = current_equity
        
        # Calculate drawdown
        drawdown = (self.peak_equity - current_equity) / self.peak_equity if self.peak_equity > 0 else 0
        
        # Check daily P&L reset
        if datetime.now().date() != self.today:
            self.today = datetime.now().date()
            self.daily_pnl = 0
        
        # Calculate daily P&L
        daily_pnl_pct = (current_equity - self.starting_equity) / self.starting_equity if self.starting_equity > 0 else 0
        
        if drawdown > self.max_daily_drawdown:
            print(f"🚨 CIRCUIT BREAKER: Drawdown {drawdown:.2%} exceeds limit {self.max_daily_drawdown:.2%}")
            return True
        
        return False
    
    def execute_trade(self, signal):
        """Execute a trade based on signal"""
        if signal is None or signal['signal'] is None:
            return None
        
        # Check circuit breaker
        if self.check_circuit_breaker():
            print("⛔ Trading halted by circuit breaker")
            return None
        
        # Check max positions
        if len(self.positions) >= self.max_positions:
            print(f"⛔ Max positions ({self.max_positions}) reached")
            return None
        
        symbol = signal['symbol']
        side = signal['signal']
        price = signal['price']
        
        # Calculate stop loss (3% for now, will use ATR later)
        if side == "BUY":
            stop_price = price * 0.97
        else:
            stop_price = price * 1.03
        
        # Get balance and calculate position size
        balance = self.get_balance()
        if balance is None:
            return None
        
        size = self.calculate_position_size(price, stop_price, balance['total'])
        
        if size <= 0:
            print(f"⚠️ Calculated position size is 0 for {symbol}")
            return None
        
        # Execute order
        try:
            order_type = 'market'
            
            if self.paper_trading:
                print(f"📝 PAPER TRADE: {side} {size:.6f} {symbol} @ {price:.2f}")
                order_id = f"paper_{int(time.time())}"
                
                # Simulate position tracking for paper trading
                position = {
                    'id': order_id,
                    'symbol': symbol,
                    'side': side,
                    'entry_price': price,
                    'size': size,
                    'stop_price': stop_price,
                    'timestamp': datetime.now().isoformat(),
                    'paper': True
                }
                self.positions.append(position)
                
                print(f"✅ PAPER TRADE EXECUTED: {side} {size:.6f} {symbol} @ ${price:.2f}")
                print(f"   Stop loss: ${stop_price:.2f}")
                
                return position
            else:
                order = self.exchange.create_market_buy_order(symbol, size) if side == "BUY" else self.exchange.create_market_sell_order(symbol, size)
                order_id = order['id']
                print(f"✅ LIVE TRADE: {side} {size:.6f} {symbol} @ {price:.2f}")
            
            # Track position
            position = {
                'id': order_id,
                'symbol': symbol,
                'side': side,
                'entry_price': price,
                'size': size,
                'stop_price': stop_price,
                'timestamp': datetime.now().isoformat(),
                'paper': self.paper_trading
            }
            self.positions.append(position)
            
            return position
            
        except Exception as e:
            print(f"❌ Error executing trade: {e}")
            return None
    
    def run(self):
        """Main trading loop"""
        print("🚀 Starting Kraken Trading Bot")
        print(f"Mode: {'PAPER' if self.paper_trading else 'LIVE'}")
        print(f"Pairs: {self.pairs}")
        print(f"Risk per trade: {self.risk_per_trade:.1%}")
        print(f"Max daily drawdown: {self.max_daily_drawdown:.1%}")
        print("-" * 50)
        
        # Get initial balance
        balance = self.get_balance()
        if balance:
            print(f"💰 Starting balance: ${balance['total']:.2f} USD")
        
        # Check for signals on all pairs
        for pair in self.pairs:
            print(f"\n📊 Analyzing {pair}...")
            signal = self.get_signal(pair)
            
            if signal:
                print(f"   RSI: {signal['rsi']:.1f} | Trend: {signal['trend']} | Signal: {signal['signal'] or 'NONE'}")
                
                if signal['signal']:
                    trade = self.execute_trade(signal)
                    if trade:
                        print(f"   ✅ Trade executed: {trade['side']} {trade['size']:.6f} @ ${trade['entry_price']:.2f}")
                else:
                    print(f"   ⏸️ No signal")
            else:
                print(f"   ⚠️ Could not generate signal")
        
        # Summary
        print("\n" + "=" * 50)
        print(f"📈 Active positions: {len(self.positions)}")
        balance = self.get_balance()
        if balance:
            pnl = balance['total'] - self.starting_equity if self.starting_equity else 0
            pnl_pct = (pnl / self.starting_equity * 100) if self.starting_equity else 0
            print(f"💰 Current equity: ${balance['total']:.2f} USD")
            print(f"📊 P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)")
        print("=" * 50)


if __name__ == "__main__":
    # Load from environment or config
    api_key = os.getenv('KRAKEN_API_KEY')
    private_key = os.getenv('KRAKEN_PRIVATE_KEY')
    
    # Or hardcode for testing (not recommended for production)
    # api_key = "your_key_here"
    # private_key = "your_secret_here"
    
    bot = KrakenTradingBot(
        api_key=api_key,
        private_key=private_key,
        paper_trading=True  # Always start with paper trading
    )
    
    bot.run()
