"""
VAYU Trading Bot - Risk Engine
==============================
Position sizing and risk management.
"""

import math
from dataclasses import dataclass
from typing import Optional

@dataclass
class Position:
    symbol: str
    side: str  # "long" or "short"
    size: float
    entry_price: float
    stop_price: float
    take_profit: float
    risk_amount: float

@dataclass
class RiskLimits:
    max_risk_per_trade: float = 0.01  # 1%
    max_daily_loss: float = 0.05  # 5%
    max_positions: int = 3
    max_leverage: float = 2.0

class RiskEngine:
    """
    Risk management engine for position sizing and trade validation.
    """
    
    def __init__(self, limits: RiskLimits = None):
        self.limits = limits or RiskLimits()
        self.daily_pnl = 0.0
        self.positions = {}
        self.daily_loss_hit = False
    
    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_price: float,
        confidence: float = 1.0
    ) -> Optional[float]:
        """
        Calculate position size based on 1% risk rule.
        
        Args:
            account_balance: Total account balance
            entry_price: Entry price
            stop_price: Stop loss price
            confidence: Signal confidence (0-1) for size adjustment
            
        Returns:
            Position size in base currency, or None if invalid
        """
        risk_amount = account_balance * self.limits.max_risk_per_trade
        
        # Adjust for confidence
        risk_amount *= confidence
        
        stop_distance = abs(entry_price - stop_price)
        if stop_distance == 0:
            return None
        
        position_size = risk_amount / stop_distance
        
        # Cap at max leverage
        max_position = (account_balance * self.limits.max_leverage) / entry_price
        position_size = min(position_size, max_position)
        
        return position_size
    
    def can_open_position(self, symbol: str) -> tuple[bool, str]:
        """
        Check if new position can be opened.
        
        Returns:
            (allowed, reason)
        """
        if self.daily_loss_hit:
            return False, "Daily loss limit hit"
        
        if len(self.positions) >= self.limits.max_positions:
            return False, f"Max positions ({self.limits.max_positions}) reached"
        
        if symbol in self.positions:
            return False, f"Already have position in {symbol}"
        
        return True, "OK"
    
    def update_daily_pnl(self, pnl: float):
        """Update daily P&L and check circuit breaker."""
        self.daily_pnl += pnl
        
        if self.daily_pnl < -self.limits.max_daily_loss:
            self.daily_loss_hit = True
    
    def add_position(self, position: Position):
        """Add position to tracking."""
        self.positions[position.symbol] = position
    
    def remove_position(self, symbol: str) -> Optional[float]:
        """Remove position and return realized P&L."""
        return self.positions.pop(symbol, None)
    
    def reset_daily(self):
        """Reset daily stats (call at market open/UTC midnight)."""
        self.daily_pnl = 0.0
        self.daily_loss_hit = False
    
    def get_status(self) -> dict:
        """Get current risk status."""
        return {
            "daily_pnl": self.daily_pnl,
            "daily_loss_hit": self.daily_loss_hit,
            "open_positions": len(self.positions),
            "position_symbols": list(self.positions.keys())
        }

if __name__ == "__main__":
    engine = RiskEngine()
    
    # Example calculation
    balance = 10000
    entry = 45000
    stop = 44000  # $1000 stop
    
    size = engine.calculate_position_size(balance, entry, stop)
    print(f"Example position sizing:")
    print(f"  Balance: ${balance:,.2f}")
    print(f"  Entry: ${entry:,.2f}")
    print(f"  Stop: ${stop:,.2f}")
    print(f"  Position size: {size:.6f} BTC")
    print(f"  Position value: ${size * entry:,.2f}")
