"""
Multi-Pair Portfolio Manager
============================
Manages multiple trading pairs with correlation filtering.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PairConfig:
    """Configuration for a trading pair."""
    symbol: str
    enabled: bool = True
    risk_weight: float = 1.0  # Relative risk allocation
    min_volume_24h: float = 1000000  # Minimum 24h volume in USD
    max_spread_pct: float = 0.001  # Maximum 0.1% spread


class PortfolioManager:
    """
    Manages multiple trading pairs with correlation-based filtering
    to avoid over-concentration in correlated assets.
    """
    
    def __init__(self, pairs_config: List[PairConfig]):
        self.pairs = {p.symbol: p for p in pairs_config}
        self.correlation_matrix: Optional[pd.DataFrame] = None
        self.price_history: Dict[str, pd.Series] = {}
        
    def add_price_data(self, symbol: str, prices: pd.Series):
        """Add historical price data for correlation calculation."""
        self.price_history[symbol] = prices
        
    def calculate_correlations(self) -> pd.DataFrame:
        """
        Calculate correlation matrix between all pairs.
        Returns DataFrame with correlation coefficients.
        """
        if len(self.price_history) < 2:
            return pd.DataFrame()
            
        # Align all price series
        df = pd.DataFrame(self.price_history)
        
        # Calculate returns
        returns = df.pct_change().dropna()
        
        # Calculate correlation matrix
        self.correlation_matrix = returns.corr()
        return self.correlation_matrix
    
    def get_correlated_pairs(self, symbol: str, threshold: float = 0.7) -> List[str]:
        """
        Get list of pairs that are highly correlated with given symbol.
        
        Args:
            symbol: Base symbol to check
            threshold: Correlation threshold (0-1)
            
        Returns:
            List of correlated pair symbols
        """
        if self.correlation_matrix is None:
            self.calculate_correlations()
            
        if symbol not in self.correlation_matrix.columns:
            return []
            
        correlations = self.correlation_matrix[symbol].abs()
        correlated = correlations[correlations > threshold].index.tolist()
        correlated.remove(symbol)  # Remove self
        
        return correlated
    
    def select_pairs_for_trading(
        self,
        max_pairs: int = 3,
        correlation_threshold: float = 0.7
    ) -> List[str]:
        """
        Select pairs for trading, filtering out highly correlated ones.
        
        Strategy:
        1. Sort by 24h volume (descending)
        2. Select top pair
        3. Skip pairs that are correlated with already selected
        4. Continue until max_pairs reached
        
        Returns:
            List of selected pair symbols
        """
        enabled_pairs = [
            sym for sym, config in self.pairs.items()
            if config.enabled
        ]
        
        if not enabled_pairs:
            return []
            
        # Calculate correlations if we have data
        if len(self.price_history) >= 2:
            self.calculate_correlations()
        
        selected = []
        
        for symbol in enabled_pairs:
            if len(selected) >= max_pairs:
                break
                
            # Check if this pair is correlated with any selected
            if self.correlation_matrix is not None:
                correlated = self.get_correlated_pairs(symbol, correlation_threshold)
                
                # Skip if correlated with any already selected
                if any(c in selected for c in correlated):
                    continue
            
            selected.append(symbol)
            
        return selected
    
    def get_position_sizes(self, total_capital: float) -> Dict[str, float]:
        """
        Calculate position sizes for each pair based on risk weights.
        
        Args:
            total_capital: Total available capital
            
        Returns:
            Dict mapping symbol to position size in USD
        """
        selected = self.select_pairs_for_trading()
        
        # Get weights for selected pairs
        weights = {
            sym: self.pairs[sym].risk_weight
            for sym in selected
        }
        
        # Normalize weights
        total_weight = sum(weights.values())
        
        if total_weight == 0:
            return {}
            
        normalized_weights = {
            sym: w / total_weight
            for sym, w in weights.items()
        }
        
        # Calculate position sizes
        position_sizes = {
            sym: total_capital * weight
            for sym, weight in normalized_weights.items()
        }
        
        return position_sizes
    
    def get_portfolio_summary(self) -> Dict:
        """Get summary of portfolio configuration."""
        return {
            'total_pairs_configured': len(self.pairs),
            'enabled_pairs': sum(1 for p in self.pairs.values() if p.enabled),
            'selected_for_trading': len(self.select_pairs_for_trading()),
            'pairs': {
                sym: {
                    'enabled': p.enabled,
                    'weight': p.risk_weight
                }
                for sym, p in self.pairs.items()
            }
        }


def create_default_portfolio() -> PortfolioManager:
    """Create portfolio with default crypto pairs."""
    pairs = [
        PairConfig("BTC/USD", risk_weight=1.5),  # Higher allocation to BTC
        PairConfig("ETH/USD", risk_weight=1.0),
        PairConfig("SOL/USD", risk_weight=0.8),
        PairConfig("ADA/USD", risk_weight=0.5),
        PairConfig("DOT/USD", risk_weight=0.5),
    ]
    return PortfolioManager(pairs)


if __name__ == "__main__":
    # Example usage
    portfolio = create_default_portfolio()
    print("Portfolio Summary:")
    print(portfolio.get_portfolio_summary())
    
    # Simulate position sizing
    sizes = portfolio.get_position_sizes(total_capital=10000)
    print("\nPosition Sizes (on $10,000):")
    for sym, size in sizes.items():
        print(f"  {sym}: ${size:,.2f}")
