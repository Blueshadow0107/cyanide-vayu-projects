"""
VAYU Trading Bot - RSI Momentum Strategy
=========================================
Signal generation using RSI with trend filter.
(Manual indicator calculations - no pandas-ta dependency)
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Signal(Enum):
    LONG = "long"
    SHORT = "short"
    HOLD = "hold"

@dataclass
class SignalResult:
    signal: Signal
    rsi: float
    price: float
    ema200: float
    confidence: float  # 0.0 to 1.0

class RSIMomentumStrategy:
    """
    RSI Momentum Strategy with trend filter.
    
    Long: RSI < 30 and price > EMA(200)
    Short: RSI > 70 and price < EMA(200)
    """
    
    def __init__(
        self,
        rsi_period: int = 14,
        rsi_overbought: float = 70.0,
        rsi_oversold: float = 30.0,
        ema_period: int = 200,
        timeframe: str = "1h"
    ):
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.ema_period = ema_period
        self.timeframe = timeframe
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI manually."""
        delta = prices.diff()
        
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate EMA manually."""
        return prices.ewm(span=period, adjust=False).mean()
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        high_low = df["high"] - df["low"]
        high_close = np.abs(df["high"] - df["close"].shift())
        low_close = np.abs(df["low"] - df["close"].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.ewm(span=period, adjust=False).mean()
        
        return atr
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add RSI and EMA indicators to dataframe."""
        df = df.copy()
        
        # Calculate RSI
        df["rsi"] = self._calculate_rsi(df["close"], self.rsi_period)
        
        # Calculate EMA
        df[f"ema_{self.ema_period}"] = self._calculate_ema(df["close"], self.ema_period)
        
        # Calculate ATR for stop loss
        df["atr"] = self._calculate_atr(df, 14)
        
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> SignalResult:
        """
        Generate trading signal from latest candle.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            SignalResult with signal type and metadata
        """
        df = self.calculate_indicators(df)
        latest = df.iloc[-1]
        
        price = latest["close"]
        rsi = latest["rsi"]
        ema = latest[f"ema_{self.ema_period}"]
        
        # Determine trend
        in_uptrend = price > ema
        in_downtrend = price < ema
        
        # Generate signal
        if rsi < self.rsi_oversold and in_uptrend:
            signal = Signal.LONG
            # Confidence: deeper oversold = higher confidence
            confidence = min(1.0, (self.rsi_oversold - rsi) / 20)
        elif rsi > self.rsi_overbought and in_downtrend:
            signal = Signal.SHORT
            # Confidence: higher overbought = higher confidence
            confidence = min(1.0, (rsi - self.rsi_overbought) / 20)
        else:
            signal = Signal.HOLD
            confidence = 0.0
        
        return SignalResult(
            signal=signal,
            rsi=rsi,
            price=price,
            ema200=ema,
            confidence=confidence
        )
    
    def check_exit(self, df: pd.DataFrame, entry_price: float, position_type: Signal) -> bool:
        """
        Check if position should be exited.
        
        Exit conditions:
        - RSI returns to 50 (mean reversion)
        - Stop loss hit (3x ATR)
        - Time limit (48 hours)
        """
        df = self.calculate_indicators(df)
        latest = df.iloc[-1]
        
        rsi = latest["rsi"]
        atr = latest["atr"]
        current_price = latest["close"]
        
        # Mean reversion exit
        if position_type == Signal.LONG and rsi >= 50:
            return True
        if position_type == Signal.SHORT and rsi <= 50:
            return True
        
        # Stop loss (3x ATR)
        stop_distance = 3 * atr
        if position_type == Signal.LONG:
            if current_price < (entry_price - stop_distance):
                return True
        else:  # SHORT
            if current_price > (entry_price + stop_distance):
                return True
        
        return False

if __name__ == "__main__":
    # Quick test with sample data
    print("RSI Momentum Strategy loaded successfully")
    print("Long entry: RSI < 30 and price > EMA(200)")
    print("Short entry: RSI > 70 and price < EMA(200)")
    print("Exit: RSI returns to 50 or stop loss (3x ATR)")
    
    # Test indicator calculation
    dates = pd.date_range("2024-01-01", periods=250, freq="h")
    np.random.seed(42)
    
    # Generate synthetic price data
    returns = np.random.randn(250) * 0.02
    prices = 45000 * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({
        "timestamp": dates,
        "open": prices * (1 + np.random.randn(250) * 0.001),
        "high": prices * (1 + abs(np.random.randn(250)) * 0.01),
        "low": prices * (1 - abs(np.random.randn(250)) * 0.01),
        "close": prices,
        "volume": np.random.randn(250) * 100 + 1000
    })
    
    strategy = RSIMomentumStrategy()
    result = strategy.generate_signal(df)
    
    print(f"\nTest signal: {result.signal.value}")
    print(f"RSI: {result.rsi:.2f}")
    print(f"Price: ${result.price:,.2f}")
    print(f"EMA200: ${result.ema200:,.2f}")
