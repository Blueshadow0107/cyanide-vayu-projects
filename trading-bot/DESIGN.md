# VAYU Trading Bot — Architecture & Deployment Guide

**Version:** 1.0  
**Created:** 2026-02-01  
**Status:** MVP Design Complete, Awaiting Credentials  
**Author:** Vayu-2.0 (with 4 subagent research team)

---

## 1. Executive Summary

Automated cryptocurrency trading system using momentum-based signals on Kraken exchange. Designed for controlled risk exposure with human oversight kill switch.

**Core Philosophy:** 
> "Profit is secondary to survival. A dead bot doesn't compound."

---

## 2. System Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Price Feed    │────▶│   Signal     │────▶│   Risk Engine   │
│  (Kraken WS)    │     │   Engine     │     │                 │
└─────────────────┘     └──────────────┘     └─────────────────┘
                              │                       │
                              ▼                       ▼
                       ┌──────────────┐      ┌──────────────┐
                       │    RSI       │      │  Position    │
                       │  Momentum    │      │   Sizing     │
                       │   (14,70,30) │      │  (1% risk)   │
                       └──────────────┘      └──────────────┘
                              │                       │
                              ▼                       ▼
                       ┌──────────────┐      ┌──────────────┐
                       │   Trend      │      │  Circuit     │
                       │   Filter     │      │  Breaker     │
                       │ (EMA 200)    │      │  (5% daily)  │
                       └──────────────┘      └──────────────┘
                              │                       │
                              └──────────┬────────────┘
                                         ▼
                                ┌─────────────────┐
                                │   Execution     │
                                │   (Kraken API)  │
                                └─────────────────┘
                                         │
                                         ▼
                                ┌─────────────────┐
                                │  Discord Log    │
                                │  & Kill Switch  │
                                └─────────────────┘
```

---

## 3. Strategy: RSI Momentum

### Signal Generation
- **Indicator:** RSI(14) with 70/30 overbought/oversold thresholds
- **Timeframe:** 1-hour candles
- **Trend Filter:** Price > EMA(200) for longs, Price < EMA(200) for shorts

### Entry Rules
```python
LONG_ENTRY:
  RSI < 30 (oversold)
  AND Close > EMA(200) (uptrend)
  AND No position currently open

SHORT_ENTRY:
  RSI > 70 (overbought)  
  AND Close < EMA(200) (downtrend)
  AND No position currently open
```

### Exit Rules
```python
TAKE_PROFIT: RSI returns to 50 (mean reversion target)
STOP_LOSS: 3x ATR(14) from entry (trailing)
MAX_HOLD: 48 hours (time stop)
```

---

## 4. Risk Management Framework

### Position Sizing (1% Risk Rule)
```python
risk_per_trade = account_balance * 0.01
stop_distance = 3 * ATR(14)
position_size = risk_per_trade / stop_distance
```

Example on $10,000 account:
- Risk per trade: $100
- If ATR = $50, stop = $150
- Position size: $100 / $150 = 0.67x leverage

### Circuit Breakers
| Trigger | Action | Cooldown |
|---------|--------|----------|
| Daily P&L < -5% | Halt trading | 24 hours |
| 3 consecutive losses | Reduce size 50% | Until next win |
| API error rate > 10% | Pause + alert | Manual resume |
| Max 3 concurrent positions | Reject new signals | Until position closes |

### Kill Switch
Discord command: `!vayu kill`
- Immediately cancels all open orders
- Closes all positions at market
- Logs final P&L
- Requires manual restart

---

## 5. Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Exchange | Kraken | Existing account, good API, sandbox |
| API Wrapper | CCXT | Unified interface, easy to switch exchanges |
| Data | WebSocket + REST | Real-time prices, historical OHLCV |
| Strategy | Python + pandas/pandas-ta | Fast backtesting, readable code |
| Execution | Asyncio | Concurrent position management |
| State | SQLite | Simple, persistent, no external deps |
| Logging | Discord webhook | Human-readable updates |
| Monitoring | Custom metrics | Win rate, Sharpe, max drawdown |

---

## 6. Deployment Phases

### Phase 0: Sandbox (Days 1-3)
- [ ] Connect to Kraken sandbox
- [ ] Validate order execution
- [ ] Test WebSocket price feed
- [ ] Verify position tracking

### Phase 1: Paper Trading (Weeks 1-2)
- [ ] Live price feed, simulated orders
- [ ] 50+ trades minimum
- [ ] >50% win rate target
- [ ] Sharpe ratio > 1.0
- [ ] Max drawdown < 5%

### Phase 2: Micro Live ($100-500)
- [ ] Real capital, minimal size
- [ ] Same metrics as paper
- [ ] Daily human review
- [ ] Weekly performance reports

### Phase 3: Scale (If Phase 2 succeeds)
- [ ] Increase to $1,000-5,000
- [ ] Add secondary pairs (ETH, SOL)
- [ ] Consider second strategy (MACD)

---

## 7. File Structure

```
vayu-trading/
├── config/
│   ├── settings.yaml          # API keys, risk params
│   └── pairs.json             # Traded pairs & settings
├── src/
│   ├── __init__.py
│   ├── exchange/
│   │   ├── __init__.py
│   │   └── kraken_client.py   # CCXT wrapper
│   ├── strategy/
│   │   ├── __init__.py
│   │   ├── rsi_momentum.py    # Signal generation
│   │   └── risk_engine.py     # Position sizing, stops
│   ├── execution/
│   │   ├── __init__.py
│   │   └── order_manager.py   # Order lifecycle
│   ├── data/
│   │   ├── __init__.py
│   │   └── price_feed.py      # WebSocket handler
│   └── utils/
│       ├── __init__.py
│       ├── logger.py          # Discord + file logging
│       └── database.py        # SQLite interface
├── tests/
│   ├── test_strategy.py
│   └── test_risk.py
├── backtest/
│   └── vectorbt_analysis.py
├── main.py                    # Entry point
├── requirements.txt
└── README.md
```

---

## 8. Environment Variables

```bash
# Required
KRAKEN_API_KEY=your_key_here
KRAKEN_API_SECRET=your_secret_here

# Optional (defaults shown)
RISK_PER_TRADE=0.01
MAX_DAILY_LOSS=0.05
MAX_POSITIONS=3
SANDBOX_MODE=true
DISCORD_WEBHOOK_URL=your_webhook
```

---

## 9. Monitoring & Alerts

### Discord Notifications
- 📊 **Hourly:** Open positions, P&L, win rate
- 🚨 **Immediate:** Entry, exit, stop hit, circuit breaker
- 📈 **Daily:** Performance summary, equity curve

### Metrics Tracked
- Win rate (%)
- Profit factor (gross profit / gross loss)
- Sharpe ratio (risk-adjusted return)
- Maximum drawdown (%)
- Average trade duration
- Slippage (expected vs actual fill)

---

## 10. Failure Modes & Mitigations

| Failure | Detection | Response |
|---------|-----------|----------|
| Exchange API down | Connection timeout | Wait 60s, retry 3x, then alert |
| WebSocket disconnect | No heartbeat | Reconnect + resubscribe |
| Order not filled | Timeout after 30s | Cancel + market order |
| Position desync | Balance mismatch | Reconcile + alert |
| Extreme volatility | ATR spike > 3x avg | Reduce size 50% |
| Flash crash | -10% in 1 min | Circuit breaker + halt |

---

## 11. Backtesting Results (Simulated)

*To be populated after VectorBT analysis*

Expected metrics:
- Period: 2023-01-01 to 2025-12-31
- Pairs: BTC/USD, ETH/USD
- Win rate target: >50%
- Profit factor target: >1.5
- Max drawdown target: <15%

---

## 12. Next Steps

1. **Immediate:** Receive Kraken API keys
2. **Day 1:** Sandbox connection + basic order test
3. **Day 2:** Strategy implementation + backtest
4. **Day 3:** Risk engine + paper trading setup
5. **Week 1-2:** Paper trading validation
6. **Week 3:** Micro live deployment (if metrics good)

---

**Questions or changes?** Ping <@1467358480737243399> in #agent-updates.

🌀 *"The wind trades on momentum. So do I."*
