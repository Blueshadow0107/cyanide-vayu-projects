"""
VAYU Trading Bot - Price Feed
=============================
Real-time and historical price data handler.
"""

import pandas as pd
from typing import List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import time

@dataclass
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    @property
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp / 1000)

class PriceFeed:
    """
    Handles price data fetching and caching.
    """
    
    def __init__(self, exchange_client):
        self.client = exchange_client
        self.cache = {}
    
    def fetch_candles(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Fetch OHLCV candles and return as DataFrame.
        
        Args:
            symbol: Trading pair (e.g., "BTC/USD")
            timeframe: Candle timeframe
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        ohlcv = self.client.get_ohlcv(symbol, timeframe, limit)
        
        df = pd.DataFrame(
            ohlcv,
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        
        # Convert timestamp to datetime
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
        
        return df
    
    def get_latest_price(self, symbol: str) -> float:
        """Get current market price."""
        ticker = self.client.get_ticker(symbol)
        return ticker["last"]
    
    def get_orderbook(self, symbol: str, limit: int = 10):
        """Get order book for spread analysis."""
        return self.client.exchange.fetch_order_book(symbol, limit)

if __name__ == "__main__":
    from kraken_client import KrakenClient
    
    print("Testing price feed...")
    client = KrakenClient(sandbox=True)
    client.load_markets()
    
    feed = PriceFeed(client)
    
    print("\nFetching BTC/USD 1h candles...")
    df = feed.fetch_candles("BTC/USD", "1h", 50)
    print(f"Got {len(df)} candles")
    print(f"Latest close: ${df['close'].iloc[-1]:,.2f}")
    print(f"Period: {df['datetime'].iloc[0]} to {df['datetime'].iloc[-1]}")
