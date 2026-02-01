# VAYU Trading Bot - Validation Runbook
=======================================

**Version:** 1.0  
**Last Updated:** 2026-02-01  
**Status:** Pre-deployment validation phase

---

## 🎯 Purpose

This runbook defines the complete validation process before deploying VAYU to live trading. No code touches real money until all checks pass.

---

## 📋 Pre-Deployment Checklist

### Phase 1: Code Review ✅
| Item | Status | Notes |
|------|--------|-------|
| Safety module (kill switch, stale data, rate limiting) | ✅ | `src/utils/safety.py` |
| Kraken client (fixed balance calc, partial fills) | ✅ | `src/exchange/kraken_client.py` |
| RSI strategy (look-ahead prevention, long/short) | ✅ | `src/strategy/rsi_momentum.py` |
| Backtest framework (VectorBT, Kraken data) | ✅ | `backtest/vectorbt_backtest.py` |

### Phase 2: Historical Validation 🔧

#### 2.1 Data Quality Check
```bash
cd trading-bot/backtest
python kraken_data_fetcher.py
```

**Expected Output:**
- [ ] Successfully fetches 2+ years of hourly BTC/USD data
- [ ] Data saved to `~/.vayu/backtest_data/`
- [ ] No gaps in data (continuous timestamps)
- [ ] OHLC values are logical (high >= low, close within range)

#### 2.2 Strategy Backtest
```bash
python vectorbt_backtest.py
```

**Minimum Requirements:**
| Metric | Threshold | Result |
|--------|-----------|--------|
| In-Sample Sharpe | > 1.0 | ___ |
| Out-of-Sample Sharpe | > 0.5 | ___ |
| Total Trades | > 50 | ___ |
| Win Rate | > 45% | ___ |
| Max Drawdown | < 20% | ___ |
| Profit Factor | > 1.3 | ___ |

#### 2.3 Walk-Forward Analysis
```python
# In Python console
from backtest.vectorbt_backtest import VAYUBacktester
bt = VAYUBacktester()

# Run walk-forward with 6mo train / 3mo test
wfa_results = bt.walk_forward_analysis(
    price,
    train_size=4320,   # 6 months of hourly
    test_size=2160,    # 3 months of hourly
    step_size=2160
)

print(f"Walk-forward consistency: {(wfa_results['test_sharpe'] > 0).mean()*100:.1f}% positive")
print(f"Sharpe StdDev: {wfa_results['test_sharpe'].std():.3f}")
```

**Requirements:**
- [ ] > 70% of windows have positive Sharpe
- [ ] Sharpe StdDev < 1.0 (low variance = robust)

---

### Phase 3: Paper Trading Simulation 📊

#### 3.1 Setup Paper Trading Environment

```bash
# Create paper trading config
cp config/config.yaml.template ~/.vayu/config.paper.yaml
```

Edit `~/.vayu/config.paper.yaml`:
```yaml
kraken:
  api_key: ""           # Leave empty for sandbox
  api_secret: ""        # Leave empty for sandbox
  sandbox: true         # MUST be true for paper

risk:
  risk_per_trade: 0.01
  max_daily_loss: 0.05
  max_positions: 3
  max_leverage: 1.0

trading:
  pairs:
    - BTC/USD
    - ETH/USD
  timeframe: 1h
```

#### 3.2 Run Paper Trading Loop

```bash
cd trading-bot
source venv/bin/activate
python main.py --mode paper --config ~/.vayu/config.paper.yaml --duration 7d
```

**Minimum Paper Trading Duration:** 7 days (168 hours)

#### 3.3 Daily Monitoring Checklist

**Day 1-3:**
- [ ] Bot starts without errors
- [ ] Price feed connects successfully
- [ ] Orders execute in paper mode (no real money)
- [ ] Kill switch works (`touch ~/.vayu/KILL`)
- [ ] Circuit breaker triggers correctly (test with small loss threshold)

**Day 4-7:**
- [ ] 20+ trades executed
- [ ] Win rate tracking accurately
- [ ] P&L calculation matches expectations
- [ ] No duplicate orders
- [ ] Partial fills handled correctly
- [ ] Stale data detection working

#### 3.4 Paper Trading Success Criteria

| Metric | Target | Minimum |
|--------|--------|---------|
| Total Trades | 50+ | 20 |
| Win Rate | 50%+ | 45% |
| Sharpe Ratio | 1.0+ | 0.5 |
| Max Drawdown | < 5% | < 10% |
| Uptime | 99%+ | 95% |

---

### Phase 4: Live Deployment Prep 🚀

#### 4.1 API Credentials
- [ ] Kraken API key generated (NO withdrawal permissions)
- [ ] API key stored in environment variable (NOT in config file)
- [ ] Sandbox disabled in config
- [ ] 2FA enabled on Kraken account

#### 4.2 Risk Limits (Final Review)
```yaml
risk:
  risk_per_trade: 0.01        # 1% max - DO NOT INCREASE
  max_daily_loss: 0.05        # 5% circuit breaker
  max_positions: 3            # Max concurrent
  max_leverage: 1.0           # NO MARGIN - hard limit
  max_account_risk: 0.10      # 10% total account at risk
```

**Vijayesh Approval Required:**
- [ ] Risk parameters reviewed and approved
- [ ] Maximum allocation signed off
- [ ] Emergency contact established

#### 4.3 Monitoring Setup
- [ ] Discord webhook configured for alerts
- [ ] SQLite database initialized (`~/.vayu/state.db`)
- [ ] Trade journal CSV path configured
- [ ] Log rotation enabled (prevent disk fill)

#### 4.4 Kill Switch Test
```bash
# Test emergency stop
touch ~/.vayu/KILL

# Verify:
# - All positions closed
# - Bot logs "KILL SWITCH ACTIVATED"
# - No new orders placed

# Reset after review:
rm ~/.vayu/KILL
```

---

## 🚨 Abort Conditions

**STOP deployment if ANY of these occur:**

| Condition | Action |
|-----------|--------|
| Backtest Sharpe < 0.5 | Redesign strategy |
| Walk-forward consistency < 50% | Strategy is overfit |
| Paper trade drawdown > 10% | Fix risk management |
| Kill switch fails test | Fix safety module |
| API errors > 10% | Debug connectivity |
| Stale data alerts > 5/day | Fix data feed |

---

## 📊 Post-Deployment Monitoring

### Week 1 (Micro Live: $100-500)
**Daily Reviews:**
- Compare live fills to expected prices (slippage analysis)
- Verify position sizing matches calculations
- Check circuit breaker hasn't triggered
- Review trade journal for anomalies

### Week 2-4 (Scale to $1000-5000)
**Weekly Reviews:**
- Sharpe ratio trending vs backtest
- Drawdown within expectations
- Win rate stabilizing
- No critical errors in logs

### Month 2+ (Full Deployment)
**Monthly Reviews:**
- Strategy performance review
- Parameter re-optimization (if needed)
- Risk limit calibration
- Code updates (if backtest shows improvements)

---

## 🔧 Emergency Procedures

### Scenario 1: Bot Gone Rogue
```bash
# Immediate stop
touch ~/.vayu/KILL

# Check positions manually on Kraken
# Close any remaining positions via Kraken UI

# Review logs
tail -f ~/.vayu/logs/trade_journal.csv
```

### Scenario 2: Exchange API Down
- Bot automatically pauses (stale data detection)
- Manual intervention after 5 minutes
- Check Kraken status page

### Scenario 3: Large Unexpected Loss
- Circuit breaker triggers automatically
- Manual review before resuming
- Check for:
  - Flash crash (temporary)
  - Strategy failure (permanent)
  - Data feed error (fixable)

---

## ✅ Sign-Off Required

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Strategy Review | Sodapoppy-Claw'd | _________ | ___ |
| Risk Approval | Vijayesh | _________ | ___ |
| Code Review | Vayu-2.0 | _________ | ___ |
| Final Go/No-Go | CyanidePopcorn | _________ | ___ |

---

**🌀 "Profit is secondary to survival. A dead bot doesn't compound."**
