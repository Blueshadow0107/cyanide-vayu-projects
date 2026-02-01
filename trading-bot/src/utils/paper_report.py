"""
VAYU Trading Bot - Paper Trading Report Generator
=================================================
Generate performance reports from paper trading logs.
"""

import json
import os
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass, asdict

@dataclass
class PaperTrade:
    timestamp: str
    symbol: str
    side: str
    entry_price: float
    exit_price: float = None
    amount: float = 0
    pnl: float = 0
    exit_reason: str = ""
    status: str = "open"  # open, closed

class PaperTradingReport:
    """
    Tracks and reports paper trading performance.
    """
    
    def __init__(self, log_file: str = "logs/paper_trades.json"):
        self.log_file = log_file
        self.trades: List[PaperTrade] = []
        self.daily_pnl = 0.0
        self.load_trades()
    
    def load_trades(self):
        """Load existing trades from disk."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.trades = [PaperTrade(**t) for t in data]
                    print(f"📚 Loaded {len(self.trades)} historical trades")
            except Exception as e:
                print(f"⚠️ Could not load trades: {e}")
    
    def save_trades(self):
        """Save trades to disk."""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, 'w') as f:
            json.dump([asdict(t) for t in self.trades], f, indent=2)
    
    def record_entry(self, symbol: str, side: str, price: float, amount: float):
        """Record a paper trade entry."""
        trade = PaperTrade(
            timestamp=datetime.now().isoformat(),
            symbol=symbol,
            side=side,
            entry_price=price,
            amount=amount,
            status="open"
        )
        self.trades.append(trade)
        self.save_trades()
        print(f"📝 Paper trade recorded: {side} {amount} {symbol} @ ${price:,.2f}")
        return len(self.trades) - 1  # Return trade index
    
    def record_exit(self, trade_index: int, exit_price: float, reason: str):
        """Record a paper trade exit."""
        if trade_index < len(self.trades):
            trade = self.trades[trade_index]
            trade.exit_price = exit_price
            trade.exit_reason = reason
            trade.status = "closed"
            
            # Calculate P&L
            if trade.side == "buy":
                trade.pnl = (exit_price - trade.entry_price) * trade.amount
            else:  # short
                trade.pnl = (trade.entry_price - exit_price) * trade.amount
            
            self.daily_pnl += trade.pnl
            self.save_trades()
            
            emoji = "🟢" if trade.pnl > 0 else "🔴"
            print(f"{emoji} Paper trade closed: {trade.symbol} P&L: ${trade.pnl:+.2f} ({reason})")
    
    def generate_report(self) -> str:
        """Generate a performance report."""
        closed_trades = [t for t in self.trades if t.status == "closed"]
        open_trades = [t for t in self.trades if t.status == "open"]
        
        if not closed_trades:
            return "📊 No closed trades yet. Paper trading in progress..."
        
        # Calculate metrics
        wins = [t for t in closed_trades if t.pnl > 0]
        losses = [t for t in closed_trades if t.pnl <= 0]
        
        win_rate = len(wins) / len(closed_trades) * 100
        total_pnl = sum(t.pnl for t in closed_trades)
        avg_win = sum(t.pnl for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t.pnl for t in losses) / len(losses) if losses else 0
        
        # Find max drawdown (simplified)
        running_pnl = 0
        max_drawdown = 0
        peak = 0
        for t in closed_trades:
            running_pnl += t.pnl
            if running_pnl > peak:
                peak = running_pnl
            drawdown = peak - running_pnl
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        report = f"""
📊 **VAYU Paper Trading Report**
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Summary:**
- Total Trades: {len(closed_trades)}
- Win Rate: {win_rate:.1f}% ({len(wins)}W / {len(losses)}L)
- Total P&L: ${total_pnl:+.2f}
- Open Positions: {len(open_trades)}

**Performance:**
- Average Win: ${avg_win:+.2f}
- Average Loss: ${avg_loss:+.2f}
- Max Drawdown: ${max_drawdown:.2f}

**Recent Trades:**
"""
        
        # Show last 5 trades
        for t in closed_trades[-5:]:
            emoji = "🟢" if t.pnl > 0 else "🔴"
            report += f"{emoji} {t.symbol} {t.side} | ${t.pnl:+.2f} | {t.exit_reason}\n"
        
        return report
    
    def print_report(self):
        """Print report to console."""
        print(self.generate_report())

if __name__ == "__main__":
    report = PaperTradingReport()
    report.print_report()
