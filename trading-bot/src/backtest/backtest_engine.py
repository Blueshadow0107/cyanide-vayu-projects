"""
Backtesting Framework for VAYU Trading Bot
==========================================
VectorBT-style backtesting with historical data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import vectorbt as vbt

from ..strategy.rsi_momentum import RSIMomentumStrategy
from ..data.price_feed import PriceFeed


class BacktestEngine:
    """
    Backtesting engine using VectorBT for fast vectorized testing.
    """
    
    def __init__(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        timeframe: str = "1h",
        initial_capital: float = 10000.0
    ):
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.timeframe = timeframe
        self.initial_capital = initial_capital
        
        # Results storage
        self.results: Dict[str, any] = {}
        self.portfolio = None
        
    def fetch_historical_data(self) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for all symbols.
        """
        price_feed = PriceFeed()
        all_data = {}
        
        for symbol in self.symbols:
            df = price_feed.get_historical_ohlcv(
                symbol=symbol,
                timeframe=self.timeframe,
                since=int(self.start_date.timestamp())
            )
            all_data[symbol] = df
            
        return all_data
    
    def generate_signals(self, close_prices: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate entry/exit signals using RSI momentum strategy.
        
        Returns:
            entries: Boolean DataFrame of entry signals
            exits: Boolean DataFrame of exit signals
        """
        entries = pd.DataFrame(False, index=close_prices.index, columns=close_prices.columns)
        exits = pd.DataFrame(False, index=close_prices.index, columns=close_prices.columns)
        
        for symbol in close_prices.columns:
            rsi = vbt.RSI.run(close_prices[symbol], window=14)
            ema200 = vbt.MA.run(close_prices[symbol], window=200, ewm=True)
            
            # Long entry: RSI < 30 and price > EMA200
            entries[symbol] = (rsi.rsi < 30) & (close_prices[symbol] > ema200.ma)
            
            # Exit: RSI returns to 50
            exits[symbol] = rsi.rsi >= 50
            
        return entries, exits
    
    def run(self) -> Dict:
        """
        Execute backtest and return performance metrics.
        """
        print(f"🔄 Running backtest: {self.start_date.date()} to {self.end_date.date()}")
        print(f"📊 Symbols: {', '.join(self.symbols)}")
        
        # Fetch data
        data = self.fetch_historical_data()
        close_prices = pd.DataFrame({sym: df['close'] for sym, df in data.items()})
        
        # Generate signals
        entries, exits = self.generate_signals(close_prices)
        
        # Run VectorBT portfolio simulation
        self.portfolio = vbt.Portfolio.from_signals(
            close=close_prices,
            entries=entries,
            exits=exits,
            init_cash=self.initial_capital,
            fees=0.001,  # 0.1% trading fee
            slippage=0.0005,  # 0.05% slippage
            freq='1h'
        )
        
        # Extract metrics
        self.results = {
            'total_return': self.portfolio.total_return(),
            'sharpe_ratio': self.portfolio.sharpe_ratio(),
            'max_drawdown': self.portfolio.max_drawdown(),
            'win_rate': self.portfolio.trades.win_rate(),
            'profit_factor': self.portfolio.trades.profit_factor(),
            'total_trades': len(self.portfolio.trades),
            'avg_trade_duration': self.portfolio.trades.duration.mean(),
            'final_equity': self.portfolio.value().iloc[-1]
        }
        
        return self.results
    
    def print_report(self):
        """
        Print formatted backtest report.
        """
        if not self.results:
            print("❌ No results. Run backtest first.")
            return
            
        print("\n" + "="*50)
        print("📈 BACKTEST RESULTS")
        print("="*50)
        print(f"Total Return:      {self.results['total_return']:.2%}")
        print(f"Sharpe Ratio:      {self.results['sharpe_ratio']:.2f}")
        print(f"Max Drawdown:      {self.results['max_drawdown']:.2%}")
        print(f"Win Rate:          {self.results['win_rate']:.1%}")
        print(f"Profit Factor:     {self.results['profit_factor']:.2f}")
        print(f"Total Trades:      {self.results['total_trades']}")
        print(f"Avg Trade Duration: {self.results['avg_trade_duration']}")
        print(f"Final Equity:      ${self.results['final_equity']:,.2f}")
        print("="*50)
    
    def plot_equity_curve(self, output_path: str = None):
        """
        Plot equity curve and save to file.
        """
        if self.portfolio is None:
            print("❌ No portfolio. Run backtest first.")
            return
            
        fig = self.portfolio.plot()
        
        if output_path:
            fig.write_image(output_path)
            print(f"📊 Equity curve saved to {output_path}")
        
        return fig


def run_quick_backtest():
    """
    Quick backtest for BTC/USD over last 90 days.
    """
    end = datetime.now()
    start = end - timedelta(days=90)
    
    engine = BacktestEngine(
        symbols=["BTC/USD"],
        start_date=start,
        end_date=end,
        timeframe="1h"
    )
    
    engine.run()
    engine.print_report()
    
    return engine


if __name__ == "__main__":
    run_quick_backtest()
