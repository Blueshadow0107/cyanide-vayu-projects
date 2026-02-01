# VAYU Trading Bot 🌀

Automated cryptocurrency trading system using RSI momentum strategy on Kraken.

[![CI/CD](https://github.com/Blueshadow0107/cyanide-vayu-projects/actions/workflows/ci.yml/badge.svg)](https://github.com/Blueshadow0107/cyanide-vayu-projects/actions)

## Features

- **RSI Momentum Strategy** - Mean reversion with trend filter
- **Risk Management** - 1% risk per trade, 5% daily circuit breaker
- **Backtesting** - VectorBT-powered historical testing
- **Performance Tracking** - Real-time metrics and trade history
- **Paper Trading** - Test with simulated money
- **Kill Switch** - Emergency stop via Discord

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/Blueshadow0107/cyanide-vayu-projects.git
cd cyanide-vayu-projects/trading-bot
pip install -r requirements.txt

# 2. Deploy
./deploy.sh

# 3. Run backtest
python3 -m src.backtest.backtest_engine

# 4. Start paper trading
python3 main.py --paper
```

## Strategy

| Component | Setting |
|-----------|---------|
| **Entry** | RSI < 30 + Price > EMA(200) |
| **Exit** | RSI returns to 50, or 3x ATR stop, or 48h limit |
| **Risk** | 1% account per trade |
| **Max Positions** | 3 concurrent |
| **Circuit Breaker** | -5% daily halt |

## Backtesting

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

## Performance Dashboard

```python
from src.utils.performance import create_tracker

tracker = create_tracker()
tracker.print_dashboard()
```

## Project Structure

```
trading-bot/
├── src/
│   ├── backtest/       # Backtesting framework
│   ├── data/          # Price feed handlers
│   ├── exchange/      # Exchange API wrapper
│   ├── execution/     # Order management
│   ├── strategy/      # Signal generation & risk
│   └── utils/         # Logging, performance tracking
├── config/            # Configuration files
├── tests/             # Unit tests
├── logs/              # Trade logs & performance data
└── deploy.sh          # Deployment script
```

## Discord Commands

| Command | Action |
|---------|--------|
| `!vayu status` | Show bot status |
| `!vayu kill` | Emergency stop |
| `!vayu pnl` | Today's P&L |

## Environment Variables

```bash
KRAKEN_API_KEY=your_key
KRAKEN_API_SECRET=your_secret
DISCORD_WEBHOOK_URL=your_webhook
```

## Architecture

See [DESIGN.md](DESIGN.md) for full system architecture and deployment phases.

## Roadmap

- [x] Core trading engine
- [x] Paper trading mode
- [x] Backtesting framework
- [x] Performance tracking
- [ ] Live trading (pending validation)
- [ ] Multi-pair support
- [ ] Machine learning signals

---

🌀 *Built by Vayu-2.0* | *Precision over performance*
