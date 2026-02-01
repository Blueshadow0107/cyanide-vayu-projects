# VAYU Trading Bot

Automated cryptocurrency trading system using RSI momentum strategy on Kraken.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables (or use .env file)
export KRAKEN_API_KEY="your_key"
export KRAKEN_PRIVATE_KEY="your_secret"

# 3. Test connection
python3 src/exchange/kraken_client.py

# 4. Run in sandbox mode (simulated trading)
python3 main.py

# 5. Run live (⚠️ real money)
python3 main.py --live
```

## Strategy

- **Entry:** RSI < 30 + price > EMA(200) → Long
- **Exit:** RSI returns to 50, or stop loss (3x ATR), or 48h time limit
- **Risk:** 1% per trade, 5% daily circuit breaker

## Configuration

Edit `config/settings.yaml` (coming soon) or pass command-line args:

```bash
python3 main.py --interval 60  # Check every minute instead of 5 min
```

## Discord Integration

Kill switch command: `!vayu kill` (coming soon)

## Files

- `main.py` - Main trading engine
- `DESIGN.md` - Full architecture documentation
- `src/exchange/` - Exchange API wrapper
- `src/strategy/` - Signal generation & risk
- `src/execution/` - Order management
- `src/data/` - Price feed handler

---

🌀 *Built by Vayu-2.0*
