"""
VAYU Trading Bot - Order Manager
================================
Order lifecycle management and execution.
"""

import time
from typing import Optional, Dict
from dataclasses import dataclass, field
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    FAILED = "failed"

@dataclass
class Trade:
    symbol: str
    side: str  # "buy" or "sell"
    amount: float
    entry_price: float
    exit_price: Optional[float] = None
    entry_time: float = field(default_factory=time.time)
    exit_time: Optional[float] = None
    pnl: Optional[float] = None
    status: str = "open"  # open, closed

class OrderManager:
    """
    Manages order execution and position tracking.
    """
    
    def __init__(self, exchange_client, risk_engine):
        self.client = exchange_client
        self.risk = risk_engine
        self.open_trades: Dict[str, Trade] = {}
        self.trade_history: list = []
    
    def enter_position(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: Optional[float] = None
    ) -> Optional[Trade]:
        """
        Enter a new position.
        
        Args:
            symbol: Trading pair
            side: "buy" (long) or "sell" (short)
            amount: Position size in base currency
            price: Limit price (None for market order)
            
        Returns:
            Trade object if successful, None if rejected
        """
        # Check risk limits
        can_trade, reason = self.risk.can_open_position(symbol)
        if not can_trade:
            print(f"❌ Trade rejected: {reason}")
            return None
        
        try:
            if price:
                # Limit order
                order = self.client.create_limit_order(symbol, side, amount, price)
                print(f"📝 Limit order placed: {side} {amount} {symbol} @ ${price}")
            else:
                # Market order
                order = self.client.create_market_order(symbol, side, amount)
                print(f"⚡ Market order executed: {side} {amount} {symbol}")
            
            entry_price = order.price if order.filled > 0 else price
            
            trade = Trade(
                symbol=symbol,
                side=side,
                amount=amount,
                entry_price=entry_price,
                status="open"
            )
            
            self.open_trades[symbol] = trade
            self.risk.add_position(trade)  # Track in risk engine
            
            return trade
            
        except Exception as e:
            print(f"❌ Order failed: {e}")
            return None
    
    def exit_position(
        self,
        symbol: str,
        price: Optional[float] = None
    ) -> Optional[float]:
        """
        Exit an open position.
        
        Returns:
            Realized P&L if successful
        """
        if symbol not in self.open_trades:
            print(f"❌ No open position for {symbol}")
            return None
        
        trade = self.open_trades[symbol]
        exit_side = "sell" if trade.side == "buy" else "buy"
        
        try:
            if price:
                order = self.client.create_limit_order(
                    symbol, exit_side, trade.amount, price
                )
            else:
                order = self.client.create_market_order(
                    symbol, exit_side, trade.amount
                )
            
            exit_price = order.price if order.filled > 0 else price
            
            # Calculate P&L
            if trade.side == "buy":
                pnl = (exit_price - trade.entry_price) * trade.amount
            else:  # short
                pnl = (trade.entry_price - exit_price) * trade.amount
            
            trade.exit_price = exit_price
            trade.exit_time = time.time()
            trade.pnl = pnl
            trade.status = "closed"
            
            # Update tracking
            del self.open_trades[symbol]
            self.risk.remove_position(symbol)
            self.risk.update_daily_pnl(pnl)
            self.trade_history.append(trade)
            
            emoji = "🟢" if pnl > 0 else "🔴"
            print(f"{emoji} Position closed: {symbol} P&L: ${pnl:+.2f}")
            
            return pnl
            
        except Exception as e:
            print(f"❌ Exit failed: {e}")
            return None
    
    def get_open_positions(self) -> Dict[str, Trade]:
        """Get all open positions."""
        return self.open_trades.copy()
    
    def cancel_all_orders(self):
        """Cancel all open orders (emergency)."""
        try:
            orders = self.client.get_open_orders()
            for order in orders:
                self.client.cancel_order(order.id, order.symbol)
                print(f"🚫 Cancelled order: {order.id}")
        except Exception as e:
            print(f"❌ Cancel failed: {e}")
    
    def emergency_close_all(self):
        """Close all positions immediately at market."""
        print("🚨 EMERGENCY CLOSE INITIATED")
        self.cancel_all_orders()
        
        for symbol in list(self.open_trades.keys()):
            self.exit_position(symbol)
        
        print("✅ All positions closed")

if __name__ == "__main__":
    from kraken_client import KrakenClient
    import sys
    sys.path.append("..")
    from strategy.risk_engine import RiskEngine, RiskLimits
    
    print("Order Manager loaded")
    print("Usage: manager.enter_position('BTC/USD', 'buy', 0.001)")
