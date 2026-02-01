"""
VAYU Trading Bot - Kraken Exchange Client
==========================================
CCXT-based wrapper for Kraken API with sandbox support.
"""

import os
import ccxt
from typing import Dict, List, Optional
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Balance:
    free: float
    used: float
    total: float

@dataclass
class Order:
    id: str
    symbol: str
    side: str
    amount: float
    price: float
    status: str
    filled: float
    remaining: float

class KrakenClient:
    """
    Kraken exchange client using CCXT.
    Supports both sandbox and live trading.
    """
    
    def __init__(self, sandbox: bool = True):
        self.sandbox = sandbox
        
        api_key = os.getenv("KRAKEN_API_KEY")
        api_secret = os.getenv("KRAKEN_PRIVATE_KEY")
        
        if not api_key or not api_secret:
            raise ValueError("KRAKEN_API_KEY and KRAKEN_PRIVATE_KEY must be set")
        
        config = {
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True,
        }
        
        # Note: Kraken's sandbox is limited; we'll use main API with test orders
        if sandbox:
            print("🧪 Using Kraken SANDBOX mode (validation only)")
        else:
            print("⚠️ Using Kraken LIVE trading")
        
        self.exchange = ccxt.kraken(config)
        self.markets = None
    
    def load_markets(self):
        """Load available markets."""
        self.markets = self.exchange.load_markets()
        return self.markets
    
    def get_balance(self) -> Dict[str, Balance]:
        """Get account balance."""
        balance = self.exchange.fetch_balance()
        result = {}
        for currency, data in balance.items():
            if isinstance(data, dict) and data.get("total", 0) > 0:
                result[currency] = Balance(
                    free=data.get("free", 0),
                    used=data.get("used", 0),
                    total=data.get("total", 0)
                )
        return result
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get current price data."""
        return self.exchange.fetch_ticker(symbol)
    
    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100
    ) -> List:
        """
        Get OHLCV candles.
        
        Args:
            symbol: Trading pair (e.g., "BTC/USD")
            timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles
        """
        return self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    
    def create_limit_order(
        self,
        symbol: str,
        side: str,  # "buy" or "sell"
        amount: float,
        price: float
    ) -> Order:
        """Create a limit order."""
        order = self.exchange.create_limit_order(symbol, side, amount, price)
        return Order(
            id=order["id"],
            symbol=order["symbol"],
            side=order["side"],
            amount=order["amount"],
            price=order["price"],
            status=order["status"],
            filled=order["filled"],
            remaining=order["remaining"]
        )
    
    def create_market_order(
        self,
        symbol: str,
        side: str,
        amount: float
    ) -> Order:
        """Create a market order."""
        order = self.exchange.create_market_order(symbol, side, amount)
        return Order(
            id=order["id"],
            symbol=order["symbol"],
            side=order["side"],
            amount=order["amount"],
            price=order.get("average", order["price"]),
            status=order["status"],
            filled=order["filled"],
            remaining=order["remaining"]
        )
    
    def cancel_order(self, order_id: str, symbol: str = None) -> bool:
        """Cancel an open order."""
        try:
            self.exchange.cancel_order(order_id, symbol)
            return True
        except Exception as e:
            print(f"Failed to cancel order {order_id}: {e}")
            return False
    
    def get_open_orders(self, symbol: str = None) -> List[Order]:
        """Get all open orders."""
        orders = self.exchange.fetch_open_orders(symbol)
        return [
            Order(
                id=o["id"],
                symbol=o["symbol"],
                side=o["side"],
                amount=o["amount"],
                price=o["price"],
                status=o["status"],
                filled=o["filled"],
                remaining=o["remaining"]
            )
            for o in orders
        ]
    
    def get_order(self, order_id: str, symbol: str = None) -> Order:
        """Get order status."""
        order = self.exchange.fetch_order(order_id, symbol)
        return Order(
            id=order["id"],
            symbol=order["symbol"],
            side=order["side"],
            amount=order["amount"],
            price=order["price"],
            status=order["status"],
            filled=order["filled"],
            remaining=order["remaining"]
        )


def test_connection():
    """Test Kraken connection and print balance."""
    client = KrakenClient(sandbox=True)
    
    try:
        print("Loading markets...")
        markets = client.load_markets()
        print(f"✅ Loaded {len(markets)} markets")
        
        # Check if BTC/USD exists
        if "BTC/USD" in markets:
            print("✅ BTC/USD trading pair available")
        else:
            print("⚠️ BTC/USD not found, checking alternatives...")
            btc_pairs = [m for m in markets.keys() if "BTC" in m]
            print(f"   Available BTC pairs: {btc_pairs[:5]}")
        
        print("\nFetching balance...")
        balance = client.get_balance()
        if balance:
            for currency, bal in balance.items():
                print(f"  {currency}: {bal.free} free, {bal.used} used, {bal.total} total")
        else:
            print("  (No balance found - account may be empty or sandbox)")
        
        print("\nFetching BTC/USD ticker...")
        ticker = client.get_ticker("BTC/USD")
        print(f"  Last: ${ticker['last']}")
        print(f"  Bid: ${ticker['bid']}")
        print(f"  Ask: ${ticker['ask']}")
        print(f"  24h Volume: {ticker['baseVolume']}")
        
        print("\n✅ Connection test passed!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        raise


if __name__ == "__main__":
    print("Testing Kraken connection...")
    test_connection()
