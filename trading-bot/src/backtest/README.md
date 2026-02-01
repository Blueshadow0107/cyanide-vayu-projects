# Backtesting Module

This directory contains the backtesting framework for the VAYU Trading Bot.

## Files

- `backtest_engine.py` - Main backtesting engine using VectorBT
- `walk_forward.py` - Walk-forward optimization (coming soon)
- `monte_carlo.py` - Monte Carlo simulation (coming soon)

## Usage

```python
from src.backtest.backtest_engine import BacktestEngine
from datetime import datetime, timedelta

engine = BacktestEngine(
    symbols=["BTC/USD", "ETH/USD"],
    start_date=datetime.now() - timedelta(days=90),
    end_date=datetime.now(),
    timeframe="1h"
)

results = engine.run()
engine.print_report()
```

## Quick Test

```bash
cd trading-bot
python -m src.backtest.backtest_engine
```
