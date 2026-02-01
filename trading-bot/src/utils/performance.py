"""
Performance Metrics Dashboard
============================
Real-time and historical performance tracking.
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TradeRecord:
    """Individual trade record."""
    symbol: str
    entry_time: datetime
    exit_time: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    side: str  # 'long' or 'short'
    size: float
    pnl: Optional[float]
    pnl_pct: Optional[float]
    exit_reason: Optional[str]


@dataclass  
class DailyStats:
    """Daily performance statistics."""
    date: str
    starting_equity: float
    ending_equity: float
    total_pnl: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    max_drawdown_pct: float


class PerformanceTracker:
    """
    Tracks and reports trading performance metrics.
    """
    
    def __init__(self, storage_path: str = "logs/performance.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.trades: List[TradeRecord] = []
        self.daily_stats: List[DailyStats] = []
        self.equity_curve: List[Dict] = []
        
        self.load_history()
    
    def load_history(self):
        """Load historical performance data."""
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                # Reconstruct trades from dict
                self.trades = [TradeRecord(**t) for t in data.get('trades', [])]
                self.daily_stats = [DailyStats(**d) for d in data.get('daily_stats', [])]
                self.equity_curve = data.get('equity_curve', [])
    
    def save_history(self):
        """Save performance data to disk."""
        data = {
            'trades': [asdict(t) for t in self.trades],
            'daily_stats': [asdict(d) for d in self.daily_stats],
            'equity_curve': self.equity_curve,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def record_trade(self, trade: TradeRecord):
        """Record a completed trade."""
        self.trades.append(trade)
        self.save_history()
    
    def record_equity(self, equity: float):
        """Record equity snapshot."""
        self.equity_curve.append({
            'timestamp': datetime.now().isoformat(),
            'equity': equity
        })
    
    def calculate_metrics(self) -> Dict:
        """Calculate overall performance metrics."""
        if not self.trades:
            return {'message': 'No trades recorded yet'}
        
        completed_trades = [t for t in self.trades if t.pnl is not None]
        
        if not completed_trades:
            return {'message': 'No completed trades yet'}
        
        wins = [t for t in completed_trades if t.pnl > 0]
        losses = [t for t in completed_trades if t.pnl <= 0]
        
        total_pnl = sum(t.pnl for t in completed_trades)
        gross_profit = sum(t.pnl for t in wins) if wins else 0
        gross_loss = abs(sum(t.pnl for t in losses)) if losses else 1  # Avoid div by zero
        
        # Calculate drawdown
        equity_values = [e['equity'] for e in self.equity_curve] if self.equity_curve else []
        max_drawdown = 0
        peak = 0
        for equity in equity_values:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        return {
            'total_trades': len(completed_trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': len(wins) / len(completed_trades) if completed_trades else 0,
            'total_pnl': total_pnl,
            'avg_pnl': total_pnl / len(completed_trades),
            'profit_factor': gross_profit / gross_loss if gross_loss > 0 else 0,
            'max_drawdown_pct': max_drawdown,
            'largest_win': max(t.pnl for t in wins) if wins else 0,
            'largest_loss': min(t.pnl for t in losses) if losses else 0,
            'avg_win': gross_profit / len(wins) if wins else 0,
            'avg_loss': sum(t.pnl for t in losses) / len(losses) if losses else 0,
        }
    
    def print_dashboard(self):
        """Print formatted performance dashboard."""
        metrics = self.calculate_metrics()
        
        print("\n" + "="*60)
        print("📊 PERFORMANCE DASHBOARD")
        print("="*60)
        
        if 'message' in metrics:
            print(f"\n{metrics['message']}")
            return
        
        print(f"\nTrade Statistics:")
        print(f"  Total Trades:     {metrics['total_trades']}")
        print(f"  Win Rate:         {metrics['win_rate']:.1%}")
        print(f"  Wins/Losses:      {metrics['winning_trades']}/{metrics['losing_trades']}")
        
        print(f"\nProfitability:")
        print(f"  Total P&L:        ${metrics['total_pnl']:,.2f}")
        print(f"  Avg P&L/Trade:    ${metrics['avg_pnl']:,.2f}")
        print(f"  Profit Factor:    {metrics['profit_factor']:.2f}")
        
        print(f"\nRisk Metrics:")
        print(f"  Max Drawdown:     {metrics['max_drawdown_pct']:.1%}")
        print(f"  Largest Win:      ${metrics['largest_win']:,.2f}")
        print(f"  Largest Loss:     ${metrics['largest_loss']:,.2f}")
        
        print("="*60)
    
    def get_recent_trades(self, n: int = 5) -> List[TradeRecord]:
        """Get N most recent trades."""
        return sorted(self.trades, key=lambda t: t.entry_time, reverse=True)[:n]


def create_tracker() -> PerformanceTracker:
    """Factory function to create a performance tracker."""
    return PerformanceTracker()
