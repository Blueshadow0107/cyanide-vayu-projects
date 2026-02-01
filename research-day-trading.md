# Day Trading Playbook
## A Comprehensive Guide to Intraday Trading Strategies

---

## Table of Contents
1. [Scalping Strategies (1-5 Min Holds)](#1-scalping-strategies)
2. [Momentum Trading](#2-momentum-trading)
3. [Range Trading](#3-range-trading)
4. [News-Based Trading](#4-news-based-trading)
5. [Intraday Technical Indicators](#5-technical-indicators)
6. [Risk Management](#6-risk-management)
7. [Pattern Recognition](#7-pattern-recognition)
8. [Daily Trading Routine](#8-daily-routine)
9. [Position Sizing Formulas](#9-position-sizing-formulas)

---

## 1. Scalping Strategies (1-5 Min Holds)

### Overview
Scalping exploits small price gaps caused by order flows or spreads. Traders aim for 5-20 cent moves with tight risk control.

### Strategy Types

#### A. Order Flow Scalping
- **Setup:** High-volume stocks with tight spreads (< $0.05)
- **Entry:** Bid/ask imbalance or Level 2 order stacking
- **Exit:** 1:1.5 risk-reward minimum or time-based (max 3 minutes)
- **Best For:** First 30 minutes after market open

#### B. VWAP Scalping
- **Setup:** Price near VWAP with directional bias
- **Long Entry:** Price touches VWAP from above with bullish candle
- **Short Entry:** Price touches VWAP from below with bearish candle
- **Stop Loss:** $0.05-0.10 beyond VWAP
- **Target:** Next key level or 2:1 R:R

#### C. Opening Range Scalping
- **Setup:** First 5-minute candle establishes range
- **Entry:** Break above high (long) or below low (short) with volume
- **Stop:** Opposite side of opening candle
- **Target:** 1.5x range width or next support/resistance

### Scalping Rules
| Rule | Specification |
|------|---------------|
| Max Hold Time | 5 minutes |
| Stop Loss | $0.05-$0.15 depending on volatility |
| Position Size | Larger size, smaller moves |
| Volume Requirement | >500K shares in first 15 min |
| Spread Requirement | < $0.05 |
| Max Loss Per Trade | 0.5% of account |

### Key Metrics
- Win rate target: 60%+
- Risk:Reward: 1:1 minimum, 1:1.5 preferred
- Daily goal: 10-20 trades
- Max daily loss: 2% of account

---

## 2. Momentum Trading

### Overview
Momentum trading captures directional moves driven by volume, news, or technical breakouts.

### Strategy Types

#### A. Breakout Trading
**Volume Breakout Entry:**
- **Setup:** Stock consolidating near highs with declining volume
- **Entry:** Break above resistance with 2x average volume
- **Confirmation:** 1-minute candle close above level
- **Stop Loss:** Below breakout level or $0.20-0.30
- **Target:** 2:1 R:R or next resistance level

**Key Breakout Levels:**
- Pre-market highs/lows
- Previous day high/low
- 52-week highs (momentum magnet)
- Whole/half dollar levels

#### B. Volume Spike Trading
- **Setup:** 3x+ average volume spike with price movement >3%
- **Entry:** Pullback to 9 EMA or VWAP after initial spike
- **Filter:** Only trade with sector momentum or news catalyst
- **Avoid:** Volume spikes into resistance without follow-through

#### C. Gap & Go
- **Setup:** Stock gapping >5% with news catalyst
- **Entry:** Break of pre-market high or opening range
- **Confirmation:** Strong first 5-minute candle (green/red body >50%)
- **Stop:** Low of first 5-min candle
- **Target:** 2:1 R:R or trailing stop below 9 EMA

### Momentum Checklist
- [ ] Clear catalyst (earnings, news, sector move)
- [ ] Above-average relative volume (>2x)
- [ ] Clean chart (no immediate overhead resistance)
- [ ] Sector alignment (stock moving with sector)
- [ ] Market conditions favorable (SPY trending)

### Red Flags
- Low float (<10M shares) with extreme moves
- No clear catalyst
- Extended from moving averages (>10% above 9 EMA)
- Heavy selling on Level 2

---

## 3. Range Trading (Support/Resistance)

### Overview
Range trading profits from price oscillations between established support and resistance levels.

### Identifying Trading Ranges
**Valid Range Requirements:**
- Minimum 2 touches on support and resistance
- Range width > 2x average true range
- Volume decreases within range
- Timeframe: 30+ minutes intraday

### Strategy Types

#### A. Support Bounce (Long)
- **Setup:** Price approaches established support level
- **Confirmation:** Reversal candle (hammer, engulfing) or Level 2 absorption
- **Entry:** Break of reversal candle high
- **Stop:** $0.10-0.20 below support
- **Target:** Middle of range or resistance
- **R:R Target:** 1:2 minimum

#### B. Resistance Rejection (Short)
- **Setup:** Price approaches established resistance
- **Confirmation:** Rejection candle (shooting star, bearish engulfing)
- **Entry:** Break of rejection candle low
- **Stop:** $0.10-0.20 above resistance
- **Target:** Middle of range or support

#### C. Range Breakout
- **Setup:** Price compressing near range boundary
- **Entry:** Close beyond level with volume expansion
- **Stop:** Middle of range
- **Target:** Range width projected from breakout point

### Support/Resistance Levels
| Level Type | Strength |
|------------|----------|
| Pre-market high/low | High |
| Opening range | High |
| Whole/half dollars | Medium-High |
| Daily pivot points | Medium |
| Previous close | Medium |
| VPOC (Volume Point of Control) | High |

### Range Trading Rules
1. Only trade confirmed ranges (2+ touches)
2. Don't trade middle of range (lowest probability)
3. Reduce size on second test (lower probability)
4. Exit immediately on range break against position
5. Avoid ranges < $0.30 width

---

## 4. News-Based Trading

### Overview
Trading scheduled and breaking news events for volatility and directional moves.

### Strategy Types

#### A. Earnings Plays
**Pre-Earnings Setup:**
- Avoid holding through earnings (gamble, not trading)
- Trade anticipation move leading into earnings
- Watch for volatility expansion (options implied volatility)

**Post-Earnings Setup:**
- Wait for initial volatility to settle (5-15 minutes)
- Trade direction of guidance/miss vs. beat
- Look for gap fill opportunities

**Earnings Entry Rules:**
- Let first 5-minute candle complete
- Enter on break of initial range
- Stop: Opposite side of initial range
- Target: 2:1 R:R or prior support/resistance

#### B. Economic Releases
**High Impact Releases:**
- FOMC announcements (2:00 PM ET)
- Non-Farm Payrolls (8:30 AM, first Friday)
- CPI/PPI data (8:30 AM)
- GDP reports

**Trading Rules:**
- No positions 2 minutes before release
- Wait for initial 1-minute candle
- Trade breakout of initial candle range
- Use half normal position size
- Wider stops due to volatility

#### C. Breaking News/Catalysts
**News Sources (Priority Order):**
1. Benzinga Pro / TradeTheNews (paid)
2. Twitter/X (verified accounts)
3. SEC filings (8-K, 13G, form 4)
4. Company press releases

**Trading Breaking News:**
- Verify news source credibility
- Check float and average volume
- Enter within first 2 minutes for momentum
- Use Level 2 for entry timing
- Take profits quickly (news fades fast)

### News Trading Checklist
- [ ] Verify news source
- [ ] Check if news is already priced in
- [ ] Analyze float and short interest
- [ ] Identify key technical levels
- [ ] Set alerts for related stocks (sympathy plays)
- [ ] Plan entry BEFORE taking trade

### Red Flags
- "Meme stock" hype without fundamentals
- Promotion/PR without substance
- Trading halt risk (circuit breakers)
- Low float + high volume = extreme volatility

---

## 5. Technical Indicators (Intraday)

### VWAP (Volume Weighted Average Price)
**What it is:** Average price weighted by volume - institutional benchmark

**Usage:**
- **Trend filter:** Above VWAP = bullish bias, below = bearish
- **Entry trigger:** Pullbacks to VWAP in trending stocks
- **Exit signal:** Break of VWAP against position

**VWAP Strategies:**
1. **VWAP Bounce:** Price pulls back to VWAP and holds - enter with trend
2. **VWAP Break:** Close below/above VWAP signals momentum shift
3. **VWAP Bands:** Standard deviation bands for overbought/oversold

### Pivot Points
**Calculation:**
- Pivot (P) = (High + Low + Close) / 3
- R1 = (2 × P) - Low
- R2 = P + (High - Low)
- S1 = (2 × P) - High
- S2 = P - (High - Low)

**Trading Pivots:**
- Use prior day data for current day levels
- R1/S1: First targets, often produce reactions
- R2/S2: Stronger levels, full exit zones
- Pivot itself: Key decision point

### Level 2 / Market Depth
**What to Watch:**
- **Bid/Ask spread:** Tighter = better liquidity
- **Size imbalance:** Large bids = support, large asks = resistance
- **Order stacking:** Multiple levels show conviction
- **Time & Sales:** Match prints to levels

**Level 2 Tactics:**
- Enter on size absorption (big orders getting eaten)
- Exit when large orders appear against your position
- Watch for "spoofing" (fake orders placed/removed)

### Moving Averages (Intraday)
**Key MA Setup:**
- 9 EMA: Short-term trend
- 20 EMA: Pullback level in strong trends
- 50 SMA: Key trend determination

**MA Strategies:**
1. **9 EMA bounce:** Enter when price touches 9 EMA in trend
2. **MA crossover:** 9/20 cross for momentum confirmation
3. **Price crossing 50 SMA:** Major trend change signal

### Relative Volume (RVOL)
**Calculation:** Current volume / Average volume at same time

**Usage:**
- RVOL > 2.0: Unusual activity, tradeable
- RVOL > 5.0: Major catalyst, high conviction
- RVOL < 1.0: Avoid, no interest

### ATR (Average True Range)
**Position Sizing Use:**
- Stop loss = 1.5x ATR
- Target = 3x ATR
- Avoid stocks with ATR < $0.20 for scalping

---

## 6. Risk Management

### The Cardinal Rules

#### Rule 1: Maximum Daily Loss
**Hard Stop:** 2% of total trading capital per day

**Implementation:**
- Calculate in dollars: Account × 0.02
- Spread across max 4 losing trades
- Walk away when hit - no exceptions

#### Rule 2: Maximum Loss Per Trade
**Standard:** 1% of account per trade
**Scalping:** 0.5% of account per trade

#### Rule 3: Risk/Reward Ratio
**Minimum:** 1:1.5 (risk $100 to make $150)
**Preferred:** 1:2 or better
**Never take:** Trades with R:R worse than 1:1

### Position Sizing

#### Fixed Dollar Risk Method
```
Position Size = (Account Risk $) / (Entry - Stop Loss)

Example:
- Account: $50,000
- Risk per trade: 1% = $500
- Entry: $50.00
- Stop: $49.50 ($0.50 risk)
- Position Size: $500 / $0.50 = 1,000 shares
```

#### Fixed Fractional Method
```
Position Size = (Account × Risk %) / (ATR × Multiplier)

Example:
- Account: $50,000
- Risk: 1%
- Stock ATR: $1.20
- Multiplier: 1.5
- Risk Amount: $1.80
- Position Size: $500 / $1.80 = 277 shares
```

### Stop Loss Types

| Type | Use Case | Placement |
|------|----------|-----------|
| Hard Stop | All trades | Fixed $ amount or technical level |
| Trailing Stop | Winning trades | Below 9 EMA or $0.20 from highs |
| Time Stop | Scalps | Exit after 5 min regardless of P&L |
| Breakeven Stop | +1R trades | Move to entry + 1 cent |

### Risk Management Checklist
- [ ] Stop loss set BEFORE entering trade
- [ ] Position size calculated
- [ ] Risk amount within daily limit
- [ ] R:R meets minimum requirement
- [ ] No more than 3 correlated positions
- [ ] Maximum 6 trades in first hour

### Psychological Stops
**When to STOP Trading for the Day:**
- 3 consecutive losses
- Emotional reaction to loss
- Deviation from trading plan
- Feeling "need" to make money back
- Distracted or tired

---

## 7. Pattern Recognition

### Bullish Patterns

#### Bull Flag
**Formation:**
- Strong upward move (pole) on high volume
- Consolidation with lower volume
- Downward sloping or parallel channel
- 5-15 candles in flag

**Entry:** Break above flag upper trendline
**Stop:** Below flag low
**Target:** Pole height added to breakout point

#### Bull Pennant
**Formation:**
- Similar to flag but with converging trendlines
- Symmetrical triangle after strong move
- Volume decreases during consolidation

**Entry:** Break above upper trendline
**Stop:** Below pennant low
**Target:** Same as flag (measured move)

#### Ascending Triangle
**Formation:**
- Flat top resistance
- Rising support trendline
- Multiple touches on both levels
- Volume decreases near apex

**Entry:** Close above resistance
**Stop:** Below support trendline
**Target:** Height of triangle added to breakout

### Bearish Patterns

#### Bear Flag
**Formation:**
- Sharp decline (pole) on high volume
- Upward consolidation channel
- Lower volume during flag

**Entry:** Break below flag lower trendline
**Stop:** Above flag high
**Target:** Pole height subtracted from breakdown point

#### Bear Pennant
**Formation:**
- Converging trendlines after decline
- Symmetrical triangle pointing down

**Entry/Stop/Target:** Mirror of bull pennant

#### Descending Triangle
**Formation:**
- Flat support level
- Declining resistance trendline
- Often continuation, sometimes reversal

**Entry:** Close below support
**Stop:** Above trendline resistance
**Target:** Triangle height subtracted from breakdown

### Reversal Patterns

#### Head and Shoulders (Intraday)
**Formation:**
- Left shoulder: First high
- Head: Higher high
- Right shoulder: Lower high (similar to left)
- Neckline: Support connecting lows

**Entry:** Break of neckline
**Stop:** Above right shoulder
**Target:** Head to neckline distance subtracted from neckline

#### Inverse Head and Shoulders
- Mirror of H&S
- Bullish reversal pattern
- Same measurements applied upward

#### Double Top/Bottom
**Double Top:**
- Two peaks at similar price
- Moderate decline between
- Break below middle low triggers entry

**Double Bottom:**
- Mirror pattern
- Two troughs at similar price
- Break above middle high triggers entry

### Pattern Trading Rules
1. **Wait for confirmation** - Don't anticipate breakouts
2. **Volume matters** - Valid patterns have volume signatures
3. **Timeframe** - Patterns more reliable on 5+ minute charts
4. **Context** - Trade with overall trend when possible
5. **Failed patterns** - Often reverse hard; keep tight stops

---

## 8. Daily Trading Routine

### Pre-Market (8:00 AM - 9:30 AM ET)

#### 8:00 - 8:30 AM: Research & Scanning
- [ ] Review overnight news and futures
- [ ] Check earnings calendar for the day
- [ ] Run gap scanner (>4% gaps)
- [ ] Review economic calendar for releases
- [ ] Note any positions held overnight

#### 8:30 - 9:15 AM: Watchlist Creation
- [ ] Select 3-5 primary watchlist stocks
- [ ] Mark key levels (premarket high/low, pivots)
- [ ] Check float and average volume
- [ ] Identify catalyst for each
- [ ] Set price alerts at key levels

#### 9:15 - 9:30 AM: Final Preparation
- [ ] Review account P&L from prior day
- [ ] Reset daily loss limit tracker
- [ ] Clear mind, prepare mentally
- [ ] Check Level 2 on watchlist stocks
- [ ] Set maximum trade count for session

### Market Open (9:30 AM - 10:30 AM)

#### First 15 Minutes (9:30 - 9:45)
- **Strategy:** Gap & Go, Opening Range Breakout
- **Rules:**
  - Wait for first 5-minute candle close
  - Only A+ setups (no forcing trades)
  - Maximum 2 trades in first 15 min
  - Tighter stops due to volatility

#### 9:45 - 10:30
- **Strategy:** Momentum continuation, VWAP trades
- **Rules:**
  - Focus on follow-through from opening range
  - Trade VWAP bounces in trending stocks
  - Scale out winners, cut losers quickly
  - Review P&L, adjust if needed

### Midday (10:30 AM - 2:00 PM)

#### 10:30 AM - 12:00 PM
- **Strategy:** Range trading, pattern setups
- **Characteristics:**
  - Lower volume, choppier price action
  - Reduce size and frequency
  - Focus on cleanest setups only
  - Work on watchlist for afternoon

#### 12:00 - 2:00 PM
- **Strategy:** Minimal trading, preparation
- **Rules:**
  - Lunch hour: typically avoid trading (12:00-1:00)
  - Prepare for power hour
  - Update scans for new setups
  - Review morning trades in journal

### Power Hour (2:00 PM - 4:00 PM)

#### 2:00 - 3:00 PM
- **Strategy:** Afternoon momentum, FOMC plays
- **Characteristics:**
  - Volume picks up
  - Afternoon trends develop
  - Look for second leg moves
  - Watch for end-of-day positioning

#### 3:00 - 3:30 PM
- **Strategy:** VWAP reversals, closing momentum
- **Rules:**
  - No new positions after 3:30 (unless closing trade)
  - Avoid holding through close unless planned
  - Scale out of profitable positions

#### 3:30 - 4:00 PM
- **Strategy:** Close positions, no new entries
- **Rules:**
  - Only closing or managing existing positions
  - Review day's performance
  - Prepare post-market analysis

### Post-Market (4:00 PM - 5:00 PM)

- [ ] Log all trades in journal
- [ ] Calculate daily P&L and statistics
- [ ] Review mistakes and lessons
- [ ] Update watchlist for next day
- [ ] Check after-hours earnings/movers

---

## 9. Position Sizing Formulas

### Basic Position Size Calculator

```
Position Size (Shares) = Account Risk ($) / (Entry Price - Stop Price)
```

### Tiered Sizing Approach

**Tier 1 (A+ Setup):**
- Risk: 1.0% of account
- Criteria: Strong trend, clear catalyst, perfect technical setup

**Tier 2 (Good Setup):**
- Risk: 0.75% of account
- Criteria: Decent setup but minor concerns

**Tier 3 (Okay Setup):**
- Risk: 0.5% of account
- Criteria: Valid setup but lower conviction

### Account Size Position Tables

#### $25,000 Account (PDT Minimum)
| Risk % | Risk $ | Stop $0.20 | Stop $0.30 | Stop $0.50 |
|--------|--------|------------|------------|------------|
| 0.5%   | $125   | 625 shares | 416 shares | 250 shares |
| 0.75%  | $187   | 935 shares | 623 shares | 374 shares |
| 1.0%   | $250   | 1,250 sh   | 833 shares | 500 shares |

#### $50,000 Account
| Risk % | Risk $ | Stop $0.20 | Stop $0.30 | Stop $0.50 |
|--------|--------|------------|------------|------------|
| 0.5%   | $250   | 1,250 sh   | 833 shares | 500 shares |
| 0.75%  | $375   | 1,875 sh   | 1,250 sh   | 750 shares |
| 1.0%   | $500   | 2,500 sh   | 1,666 sh   | 1,000 sh   |

#### $100,000 Account
| Risk % | Risk $ | Stop $0.20 | Stop $0.30 | Stop $0.50 |
|--------|--------|------------|------------|------------|
| 0.5%   | $500   | 2,500 sh   | 1,666 sh   | 1,000 sh   |
| 0.75%  | $750   | 3,750 sh   | 2,500 sh   | 1,500 sh   |
| 1.0%   | $1,000 | 5,000 sh   | 3,333 sh   | 2,000 sh   |

### Volatility-Based Sizing

```
ATR = Average True Range (14-period)
Risk per Share = ATR × 1.5
Position Size = (Account × Risk%) / Risk per Share

Example:
- Account: $50,000
- Risk %: 1% ($500)
- Stock ATR: $0.80
- Risk per Share: $0.80 × 1.5 = $1.20
- Position Size: $500 / $1.20 = 416 shares
```

### Scaling In Formula

**Two-Entry Scale:**
- First entry: 50% of planned position
- Second entry: 50% at better price or on confirmation
- Both entries use same stop loss
- Average price = ((P1 × 0.5) + (P2 × 0.5))

**Pyramiding (Adding to Winners):**
- Only add to winning positions (+1R or more)
- Move stop to breakeven on first position first
- Never add more total risk than initial trade risk
- Maximum 3 scale-in levels

---

## Quick Reference Cards

### Entry Checklist
- [ ] Setup meets strategy criteria
- [ ] Risk/Reward is 1:1.5 or better
- [ ] Position size calculated
- [ ] Stop loss identified
- [ ] Target price identified
- [ ] Catalyst or reason for move
- [ ] Volume is above average
- [ ] No conflicting market conditions

### Exit Rules
**Take Profit When:**
- Target reached
- Risk/Reward hits 2:1 or 3:1
- Technical level reached
- Volume dries up
- Pattern completes
- End of session approaching

**Cut Loss When:**
- Stop loss hit (no exceptions)
- Original thesis invalidated
- Pattern fails
- Volume contradicts direction
- Better opportunity elsewhere (opportunity cost)

### Daily Goals
- **Profit Target:** 1-2% of account
- **Max Loss:** 2% of account (hard stop)
- **Win Rate Target:** 50%+ (with 1:2 R:R)
- **Trade Count:** 5-15 trades per day
- **Green Days Target:** 60%+ of trading days

### Market Condition Adjustments

| Condition | Action |
|-----------|--------|
| SPY trending up | Increase long exposure, wider stops |
| SPY trending down | Focus on shorts, reduce size |
| SPY chopping | Reduce size, tighten stops, fewer trades |
| High VIX (>25) | Reduce position size by 50% |
| Low VIX (<15) | Expect smaller moves, lower targets |
| Earnings season | More gap plays, wider initial stops |

---

## Disclaimer

**Trading involves substantial risk of loss.** This playbook is for educational purposes only and does not constitute financial advice. Past performance is not indicative of future results. Always risk capital you can afford to lose.

**Key Reminders:**
- Start with paper trading (simulation)
- Never risk more than you can afford to lose
- Most day traders lose money - proper education and discipline are essential
- Consider working with a tax professional for trader tax status

---

*Last Updated: February 2026*
