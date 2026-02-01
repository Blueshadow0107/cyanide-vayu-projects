"""
VAYU Trading Bot - Kraken Historical Data Fetcher
==================================================
Fetch OHLCV data directly from Kraken for backtesting.
No yfinance limitations — get full historical range.
"""

import ccxt
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KrakenDataFetcher:
    """
    Fetch historical OHLCV data from Kraken exchange.
    
    Kraken limits:
    - 720 candles per request for most timeframes
    - Rate limit: ~1 request per second for public endpoints
    """
    
    def __init__(self):
        self.exchange = ccxt.kraken({'enableRateLimit': True})
        self.data_dir = Path.home() / ".vayu" / "backtest_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1h',
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        save: bool = True
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data from Kraken.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USD')
            timeframe: Candle timeframe ('1m', '5m', '15m', '1h', '4h', '1d', '1w')
            since: Start datetime
            until: End datetime (default: now)
            save: Save to disk for caching
        
        Returns:
            DataFrame with OHLCV data
        """
        if until is None:
            until = datetime.now()
        
        if since is None:
            since = until - timedelta(days=730)  # Default 2 years
        
        since_ms = int(since.timestamp() * 1000)
        until_ms = int(until.timestamp() * 1000)
        
        logger.info(f"Fetching {symbol} {timeframe} from {since} to {until}")
        
        all_candles = []
        current_since = since_ms
        
        # Kraken returns max 720 candles per request
        while current_since < until_ms:
            try:
                candles = self.exchange.fetch_ohlcv(
                    symbol,
                    timeframe,
                    since=current_since,
                    limit=720
                )
                
                if not candles:
                    break
                
                all_candles.extend(candles)
                
                # Update since to last candle + 1ms
                current_since = candles[-1][0] + 1
                
                # Rate limiting
                time.sleep(1.1)
                
                logger.debug(f"Fetched {len(candles)} candles, total: {len(all_candles)}")
                
                # Break if we got less than limit (reached end)
                if len(candles) < 720:
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching data: {e}")
                time.sleep(5)
                continue
        
        if not all_candles:
            raise ValueError(f"No data returned for {symbol}")
        
        # Convert to DataFrame
        df = pd.DataFrame(
            all_candles,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # Filter to requested range
        df = df[(df.index >= since) & (df.index <= until)]
        
        logger.info(f"Total candles fetched: {len(df)}")
        
        # Save to disk
        if save:
            self._save_data(df, symbol, timeframe)
        
        return df
    
    def _save_data(self, df: pd.DataFrame, symbol: str, timeframe: str):
        """Save data to disk for caching."""
        # Clean symbol for filename
        safe_symbol = symbol.replace('/', '_')
        filename = f"{safe_symbol}_{timeframe}.csv"
        filepath = self.data_dir / filename
        
        df.to_csv(filepath, index=False)
        logger.info(f"Saved to {filepath}")
    
    def load_cached(
        self,
        symbol: str,
        timeframe: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Optional[pd.DataFrame]:
        """
        Load cached data if available and fresh.
        
        Returns:
            DataFrame or None if cache miss
        """
        safe_symbol = symbol.replace('/', '_')
        filename = f"{safe_symbol}_{timeframe}.csv"
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            return None
        
        df = pd.read_csv(filepath)
        
        # Check if data covers requested range
        if since and df.index[0] > since:
            return None  # Cache doesn't go back far enough
        if until and df.index[-1] < until:
            return None  # Cache doesn't go forward far enough
        
        # Filter to requested range
        if since:
            df = df[df.index >= since]
        if until:
            df = df[df.index <= until]
        
        logger.info(f"Loaded cached data: {len(df)} bars")
        return df
    
    def fetch_or_load(
        self,
        symbol: str,
        timeframe: str = '1h',
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Load from cache if available, otherwise fetch from Kraken.
        """
        # Try cache first
        cached = self.load_cached(symbol, timeframe, since, until)
        if cached is not None:
            return cached
        
        # Fetch fresh
        return self.fetch_ohlcv(symbol, timeframe, since, until)
    
    def get_available_pairs(self) -> List[str]:
        """Get list of available trading pairs on Kraken."""
        markets = self.exchange.load_markets()
        usd_pairs = [s for s in markets.keys() if s.endswith('/USD')]
        return sorted(usd_pairs)


def test_fetch():
    """Test the data fetcher."""
    fetcher = KrakenDataFetcher()
    
    print("VAYU Kraken Data Fetcher Test")
    print("=" * 60)
    
    # Show available pairs
    print("\nAvailable USD pairs (sample):")
    pairs = fetcher.get_available_pairs()
    for p in pairs[:10]:
        print(f"  {p}")
    print(f"  ... and {len(pairs)-10} more")
    
    # Fetch 1 year of hourly BTC data
    print("\nFetching BTC/USD 1h data (last 365 days)...")
    until = datetime.now()
    since = until - timedelta(days=365)
    
    try:
        df = fetcher.fetch_ohlcv('BTC/USD', '1h', since, until)
        print(f"\nData summary:")
        print(f"  Bars: {len(df)}")
        print(f"  From: {df.index[0]}")
        print(f"  To: {df.index[-1]}")
        print(f"\nFirst 3 bars:")
        print(df.head(3))
        print(f"\nLast 3 bars:")
        print(df.tail(3))
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_fetch()
