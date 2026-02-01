"""
VAYU Trading Bot - VectorBT Backtest Framework
================================================
Proper backtesting with:
- Look-ahead bias prevention (shift indicators)
- Parameter optimization
- Out-of-sample validation
- Walk-forward analysis
"""

import vectorbt as vbt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import yaml
from typing import Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VAYUBacktester:
    """
    VectorBT-based backtest framework for RSI momentum strategy.
    
    Key feature: Proper look-ahead bias prevention by shifting signals.
    """
    
    def __init__(self, config_path: str = "~/.vayu/config.yaml"):
        self.config = self._load_config(config_path)
        self.price_data = {}
        self.results = {}
    
    def _load_config(self, path: str) -> Dict:
        """Load configuration."""
        path = Path(path).expanduser()
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f)
        return {}
    
    def load_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        timeframe: str = '1h'
    ) -> pd.Series:
        """
        Load historical price data.
        
        For now, uses yfinance. Replace with Kraken historical data fetch.
        """
        import yfinance as yf
        
        ticker_map = {
            'BTC/USD': 'BTC-USD',
            'ETH/USD': 'ETH-USD'
        }
        
        ticker = ticker_map.get(symbol, symbol)
        
        logger.info(f"Loading data for {symbol} ({ticker}) from {start_date} to {end_date}")
        
        df = yf.download(ticker, start=start_date, end=end_date, interval=timeframe)
        
        if df.empty:
            raise ValueError(f"No data returned for {symbol}")
        
        # Handle multi-index columns from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        price = df['Close']
        self.price_data[symbol] = price
        
        logger.info(f"Loaded {len(price)} bars")
        return price
    
    def calculate_rsi(self, price: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI using pandas-ta or manual method."""
        try:
            import pandas_ta as ta
            rsi = ta.rsi(price, length=period)
        except ImportError:
            # Manual RSI calculation (Wilder's method)
            delta = price.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
            avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_ema(self, price: pd.Series, period: int = 200) -> pd.Series:
        """Calculate EMA."""
        return price.ewm(span=period, adjust=False).mean()
    
    def generate_signals(
        self,
        price: pd.Series,
        rsi_period: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
        ema_period: int = 200,
        prevent_lookahead: bool = True
    ) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        """
        Generate entry and exit signals.
        
        Args:
            price: Price series
            rsi_period: RSI lookback
            rsi_oversold: Entry threshold (long)
            rsi_overbought: Entry threshold (short)
            ema_period: Trend filter period
            prevent_lookahead: If True, shift signals to prevent look-ahead bias
        
        Returns:
            (long_entries, long_exits, short_entries, short_exits) boolean series
        """
        # Calculate indicators
        rsi = self.calculate_rsi(price, rsi_period)
        ema = self.calculate_ema(price, ema_period)
        
        # Trend filter
        in_uptrend = price > ema
        in_downtrend = price < ema
        
        # Entry signals (raw)
        long_entry_raw = (rsi < rsi_oversold) & in_uptrend
        short_entry_raw = (rsi > rsi_overbought) & in_downtrend
        
        # Exit signals (raw) - RSI mean reversion to 50
        # Long exit: RSI crosses above 50 (from below)
        long_exit_raw = (rsi > 50) & (rsi.shift(1) <= 50)
        # Short exit: RSI crosses below 50 (from above)  
        short_exit_raw = (rsi < 50) & (rsi.shift(1) >= 50)
        
        # LOOK-AHEAD BIAS PREVENTION
        # Shift signals by 1 to simulate executing on NEXT bar's open
        if prevent_lookahead:
            long_entries = long_entry_raw.shift(1).fillna(False)
            long_exits = long_exit_raw.shift(1).fillna(False)
            short_entries = short_entry_raw.shift(1).fillna(False)
            short_exits = short_exit_raw.shift(1).fillna(False)
            logger.info("Look-ahead bias prevention: signals shifted by 1 bar")
        else:
            long_entries = long_entry_raw
            long_exits = long_exit_raw
            short_entries = short_entry_raw
            short_exits = short_exit_raw
        
        return long_entries, long_exits, short_entries, short_exits
    
    def run_backtest(
        self,
        price: pd.Series,
        long_entries: pd.Series,
        long_exits: pd.Series,
        short_entries: pd.Series = None,
        short_exits: pd.Series = None,
        init_cash: float = 10000,
        fees: float = 0.001,  # 0.1%
        slippage: float = 0.001,  # 0.1%
        freq: str = '1h'
    ) -> vbt.Portfolio:
        """
        Run VectorBT backtest with long/short support.
        
        Args:
            price: Price series
            long_entries: Long entry signals
            long_exits: Long exit signals
            short_entries: Short entry signals (optional)
            short_exits: Short exit signals (optional)
            init_cash: Starting capital
            fees: Commission per trade (0.001 = 0.1%)
            slippage: Slippage estimate
            freq: Data frequency for Sharpe calc
        """
        portfolio = vbt.Portfolio.from_signals(
            price,
            entries=long_entries,
            exits=long_exits,
            short_entries=short_entries,
            short_exits=short_exits,
            init_cash=init_cash,
            fees=fees,
            slippage=slippage,
            freq=freq
        )
        
        return portfolio
    
    def optimize_parameters(
        self,
        price: pd.Series,
        rsi_windows: range = range(7, 21, 2),
        oversold_range: range = range(20, 36, 5),
        overbought_range: range = range(65, 81, 5),
        metric: str = 'sharpe_ratio'
    ) -> pd.DataFrame:
        """
        Grid search for optimal parameters.
        
        Returns:
            DataFrame with results for each parameter combination
        """
        results = []
        
        total_combos = len(rsi_windows) * len(oversold_range) * len(overbought_range)
        logger.info(f"Testing {total_combos} parameter combinations...")
        
        for rsi_p in rsi_windows:
            for oversold in oversold_range:
                for overbought in overbought_range:
                    long_entries, long_exits, short_entries, short_exits = self.generate_signals(
                        price, rsi_p, oversold, overbought,
                        prevent_lookahead=True
                    )
                    
                    pf = self.run_backtest(
                        price, long_entries, long_exits, 
                        short_entries, short_exits
                    )
                    
                    stats = pf.stats()
                    
                    results.append({
                        'rsi_period': rsi_p,
                        'oversold': oversold,
                        'overbought': overbought,
                        'total_return': stats.get('Total Return [%]', 0),
                        'sharpe_ratio': stats.get('Sharpe Ratio', 0),
                        'max_drawdown': stats.get('Max Drawdown [%]', 0),
                        'trades': stats.get('Total Trades', 0),
                        'win_rate': stats.get('Win Rate [%]', 0),
                        'profit_factor': stats.get('Profit Factor', 0)
                    })
        
        df = pd.DataFrame(results)
        
        # Sort by metric
        if metric in df.columns:
            df = df.sort_values(metric, ascending=False)
        
        return df
    
    def walk_forward_analysis(
        self,
        price: pd.Series,
        train_size: int = 500,  # bars
        test_size: int = 100,   # bars
        step_size: int = 100,
        **strategy_params
    ) -> pd.DataFrame:
        """
        Walk-forward optimization.
        
        Train on train_size bars, test on test_size bars, roll forward.
        """
        results = []
        
        n = len(price)
        start = 0
        window_num = 0
        
        while start + train_size + test_size <= n:
            window_num += 1
            train_end = start + train_size
            test_end = train_end + test_size
            
            # Training data
            train_price = price.iloc[start:train_end]
            
            # Test data
            test_price = price.iloc[train_end:test_end]
            
            # Optimize on training
            opt_df = self.optimize_parameters(
                train_price,
                rsi_windows=range(10, 21, 2),  # Reduced for speed
                oversold_range=range(25, 36, 5),
                overbought_range=range(65, 76, 5)
            )
            
            if len(opt_df) == 0:
                start += step_size
                continue
            
            # Get best params
            best = opt_df.iloc[0]
            
            # Test on out-of-sample
            long_entries, long_exits, short_entries, short_exits = self.generate_signals(
                test_price,
                rsi_period=int(best['rsi_period']),
                rsi_oversold=best['oversold'],
                rsi_overbought=best['overbought'],
                prevent_lookahead=True
            )
            
            pf = self.run_backtest(
                test_price, long_entries, long_exits,
                short_entries, short_exits
            )
            stats = pf.stats()
            
            results.append({
                'window': window_num,
                'train_start': str(train_price.index[0]),
                'train_end': str(train_price.index[-1]),
                'test_start': str(test_price.index[0]),
                'test_end': str(test_price.index[-1]),
                'best_rsi_period': best['rsi_period'],
                'best_oversold': best['oversold'],
                'best_overbought': best['overbought'],
                'train_sharpe': best['sharpe_ratio'],
                'test_total_return': stats.get('Total Return [%]', 0),
                'test_sharpe': stats.get('Sharpe Ratio', 0),
                'test_max_dd': stats.get('Max Drawdown [%]', 0),
                'test_trades': stats.get('Total Trades', 0)
            })
            
            logger.info(f"Window {window_num}: Train Sharpe={best['sharpe_ratio']:.2f}, "
                       f"Test Sharpe={stats.get('Sharpe Ratio', 0):.2f}")
            
            start += step_size
        
        return pd.DataFrame(results)
    
    def analyze_results(self, portfolio: vbt.Portfolio, name: str = "Backtest"):
        """Print and return key metrics."""
        stats = portfolio.stats()
        
        print(f"\n{'='*60}")
        print(f"{name} Results")
        print(f"{'='*60}")
        print(f"Total Return:     {stats.get('Total Return [%]', 0):.2f}%")
        print(f"Sharpe Ratio:     {stats.get('Sharpe Ratio', 0):.3f}")
        print(f"Max Drawdown:     {stats.get('Max Drawdown [%]', 0):.2f}%")
        print(f"Total Trades:     {stats.get('Total Trades', 0)}")
        print(f"Win Rate:         {stats.get('Win Rate [%]', 0):.1f}%")
        print(f"Profit Factor:    {stats.get('Profit Factor', 0):.2f}")
        print(f"Avg Trade:        {stats.get('Avg Winning Trade [%]', 0):.2f}%")
        print(f"{'='*60}\n")
        
        return stats


def main():
    """Example backtest workflow."""
    print("VAYU Backtest Framework")
    print("=" * 60)
    
    bt = VAYUBacktester()
    
    # Load data
    price = bt.load_data('BTC/USD', '2023-01-01', '2025-01-01', '1h')
    
    # Split for OOS validation
    split_idx = int(len(price) * 0.7)
    train_price = price.iloc[:split_idx]
    test_price = price.iloc[split_idx:]
    
    print(f"\nIn-sample:  {len(train_price)} bars")
    print(f"Out-of-sample: {len(test_price)} bars")
    
    # Optimize on training data
    print("\n" + "=" * 60)
    print("OPTIMIZATION (In-Sample)")
    print("=" * 60)
    
    opt_results = bt.optimize_parameters(
        train_price,
        rsi_windows=range(10, 21, 2),
        oversold_range=range(25, 36, 5),
        overbought_range=range(65, 76, 5)
    )
    
    print("\nTop 5 parameter sets:")
    print(opt_results.head())
    
    # Test best params on OOS
    best = opt_results.iloc[0]
    print(f"\nBest params: RSI({best['rsi_period']}), "
          f"oversold={best['oversold']}, overbought={best['overbought']}")
    
    # In-sample backtest with best params
    le_train, lx_train, se_train, sx_train = bt.generate_signals(
        train_price,
        rsi_period=int(best['rsi_period']),
        rsi_oversold=best['oversold'],
        rsi_overbought=best['overbought'],
        prevent_lookahead=True
    )
    
    pf_train = bt.run_backtest(train_price, le_train, lx_train, se_train, sx_train)
    bt.analyze_results(pf_train, "In-Sample")
    
    # Out-of-sample backtest
    print("=" * 60)
    print("OUT-OF-SAMPLE VALIDATION")
    print("=" * 60)
    
    le_test, lx_test, se_test, sx_test = bt.generate_signals(
        test_price,
        rsi_period=int(best['rsi_period']),
        rsi_oversold=best['oversold'],
        rsi_overbought=best['overbought'],
        prevent_lookahead=True
    )
    
    pf_test = bt.run_backtest(test_price, le_test, lx_test, se_test, sx_test)
    bt.analyze_results(pf_test, "Out-of-Sample")
    
    # Walk-forward analysis
    print("=" * 60)
    print("WALK-FORWARD ANALYSIS")
    print("=" * 60)
    
    wfa_results = bt.walk_forward_analysis(
        price,
        train_size=1000,
        test_size=200,
        step_size=200
    )
    
    print(f"\nWalk-forward results ({len(wfa_results)} windows):")
    print(f"Avg Test Sharpe: {wfa_results['test_sharpe'].mean():.3f}")
    print(f"Sharpe StdDev:   {wfa_results['test_sharpe'].std():.3f}")
    print(f"Consistency:     {(wfa_results['test_sharpe'] > 0).mean()*100:.1f}% positive")
    
    print("\n" + "=" * 60)
    print("BACKTEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
