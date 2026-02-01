# Trading Bot Infrastructure Research Report

## Executive Summary

This report covers the essential infrastructure components for building algorithmic trading bots: broker APIs, Python libraries, data sources, and execution models. Focus is on free/cheap options suitable for retail traders and small-scale operations.

---

## 1. Broker APIs for Algorithmic Trading

### 1.1 Alpaca (Recommended for Beginners)

**Overview:** Commission-free API-first brokerage specifically designed for algorithmic trading.

**Pricing:**
| Feature | Free Tier | Paid Tier |
|---------|-----------|-----------|
| Commission | $0 | $0 |
| API Calls | 200/min | 10,000/min |
| Real-time Data | 15-min delayed | Real-time via websocket |
| Historical Data | 7+ years | 7+ years |
| WebSocket Symbols | Limited to 30 | Unlimited |
| Options Data | Indicative | Real-time (OPRA) |

**Key Features:**
- REST API and WebSocket streaming
- Paper trading environment
- Extended hours trading (4:00am - 8:00pm ET)
- Fractional shares support
- US Stocks, ETFs, Options, and Crypto

**Rate Limits:**
- Free: 200 API calls per minute
- Paid: 10,000 API calls per minute
- WebSocket: 30 symbols (free), unlimited (paid)

**Python SDK Example:**
```python
import alpaca_trade_api as tradeapi

# Initialize API
api = tradeapi.REST('API_KEY', 'SECRET_KEY', base_url='https://paper-api.alpaca.markets')

# Submit market order
api.submit_order(
    symbol='AAPL',
    qty=10,
    side='buy',
    type='market',
    time_in_force='day'
)

# Submit limit order
api.submit_order(
    symbol='TSLA',
    qty=5,
    side='buy',
    type='limit',
    time_in_force='gtc',
    limit_price=150.00
)

# Get account info
account = api.get_account()
print(f"Buying Power: ${account.buying_power}")

# Stream real-time data
conn = tradeapi.stream2.StreamConn('API_KEY', 'SECRET_KEY')

@conn.on(r'A$')
async def on_trade(conn, channel, data):
    print(f"Trade: {data.symbol} @ ${data.price}")

conn.run(['alpacadata.v1.trades'])
```

**Pros:**
- True commission-free trading
- Excellent documentation
- Active community
- Paper trading included

**Cons:**
- Only US markets
- Rate limits on free tier
- No forex or international stocks

---

### 1.2 Interactive Brokers (IBKR)

**Overview:** Professional-grade broker with extensive global market access.

**Pricing:**
| Plan | Tiered | Fixed | IBKR Lite |
|------|--------|-------|-----------|
| US Stocks | $0.0035/share (min $0.35) | $0.005/share (min $1.00) | $0 (US residents only) |
| Options | $0.65/contract | $0.65/contract | $0.65/contract |
| Monthly Volume Discounts | Yes | No | No |

**Additional Fees:**
- SEC Fee: $0.000008 * trade value
- FINRA TAF: $0.000195 * quantity sold (max $7.27)

**Key Features:**
- 150+ global markets
- Stocks, Options, Futures, Forex, Bonds, Crypto
- Trader Workstation (TWS) API
- IB Gateway for headless operation
- Market depth data

**Python SDK (ib_insync):**
```python
from ib_insync import *

# Connect to IB Gateway or TWS
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)  # 7497 for IB Gateway, 7496 for TWS

# Define contract
contract = Stock('AAPL', 'SMART', 'USD')

# Get market data
bars = ib.reqHistoricalData(
    contract,
    endDateTime='',
    durationStr='1 D',
    barSizeSetting='1 min',
    whatToShow='TRADES',
    useRTH=True
)

# Create DataFrame
df = util.df(bars)
print(df)

# Submit market order
order = MarketOrder('BUY', 100)
trade = ib.placeOrder(contract, order)

# Submit limit order
limit_order = LimitOrder('BUY', 100, 150.00)
trade = ib.placeOrder(contract, limit_order)

# Callback for order status
def on_order_status(trade):
    print(f"Order {trade.order.orderId} status: {trade.orderStatus.status}")

trade.fillEvent += on_order_status

# Disconnect
ib.disconnect()
```

**Pros:**
- Global market access (150+ exchanges)
- Lowest cost for high volume
- Professional-grade tools
- Excellent for forex and futures

**Cons:**
- Steep learning curve
- Complex API
- No true commission-free tier (except IBKR Lite, US only)

---

### 1.3 Binance (Crypto Only)

**Overview:** World's largest crypto exchange by volume with comprehensive API.

**Pricing:**
| Feature | Spot | Futures |
|---------|------|---------|
| Maker Fee | 0.1% | 0.02% |
| Taker Fee | 0.1% | 0.05% |
| With BNB (25% discount) | 0.075% | 0.015% maker / 0.0375% taker |
| VIP Discount | Up to 0.015% maker | Up to 0% maker |

**API Limits:**
- Spot API: 1,200 request weight per minute
- Futures API: 2,400 request weight per minute
- WebSocket: Unlimited streams

**Key Features:**
- 600+ cryptocurrencies
- Spot, Margin, Futures, Options
- Earn/staking products
- Binance Pay
- Low fees

**Python SDK (python-binance):**
```python
from binance.client import Client
from binance.enums import *

# Initialize
client = Client('api_key', 'api_secret')

# Get account info
account = client.get_account()
balances = [b for b in account['balances'] if float(b['free']) > 0]

# Get historical klines (OHLCV)
klines = client.get_historical_klines(
    "BTCUSDT",
    Client.KLINE_INTERVAL_1HOUR,
    "1 month ago UTC"
)

# Place market buy order
order = client.order_market_buy(
    symbol='BTCUSDT',
    quantity=0.001
)

# Place limit order
limit_order = client.order_limit_buy(
    symbol='ETHUSDT',
    quantity=0.01,
    price=1800.00
)

# WebSocket for real-time data
from binance import ThreadedWebsocketManager

def handle_socket_message(msg):
    print(f"Price: {msg['c']}")

twm = ThreadedWebsocketManager(api_key='api_key', api_secret='api_secret')
twm.start()
twm.start_kline_socket(callback=handle_socket_message, symbol='BTCUSDT')
```

**Pros:**
- Lowest fees in crypto
- Massive liquidity
- Extensive API features
- Futures and margin trading

**Cons:**
- Crypto only
- Regulatory issues in some jurisdictions
- API can be complex

---

### 1.4 Broker Comparison Summary

| Feature | Alpaca | IBKR | Binance |
|---------|--------|------|---------|
| Commission | $0 | $0-$0.005/share | 0.075-0.1% |
| Markets | US Only | Global | Crypto Only |
| Best For | Beginners | Professionals | Crypto Traders |
| API Ease | Easy | Complex | Moderate |
| Paper Trading | Yes | Yes | Testnet |
| Extended Hours | Yes | Yes | 24/7 |

---

## 2. Python Libraries for Trading

### 2.1 Backtrader

**Overview:** Feature-rich, open-source backtesting framework.

**Key Features:**
- Event-driven backtesting
- 122+ built-in indicators
- Multiple data feeds and timeframes
- Integrated broker simulation
- Plotting with matplotlib
- Live trading with IB, Oanda, Alpaca

**Installation:**
```bash
pip install backtrader
pip install backtrader[plotting]  # With matplotlib support
```

**Basic Strategy Example:**
```python
import backtrader as bt
import datetime

class SmaCross(bt.SignalStrategy):
    params = (
        ('pfast', 10),
        ('pslow', 30),
    )
    
    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)
        sma2 = bt.ind.SMA(period=self.p.pslow)
        self.signal_add(bt.SIGNAL_LONG, bt.ind.CrossOver(sma1, sma2))

# Create cerebro engine
cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross)

# Add data
data = bt.feeds.YahooFinanceData(
    dataname='AAPL',
    fromdate=datetime.datetime(2020, 1, 1),
    todate=datetime.datetime(2023, 1, 1)
)
cerebro.adddata(data)

# Configure broker
cerebro.broker.setcash(10000.0)
cerebro.broker.setcommission(commission=0.001)  # 0.1%

# Add analyzers
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

# Run backtest
results = cerebro.run()
strat = results[0]

# Print results
print(f"Final Value: ${cerebro.broker.getvalue():.2f}")
print(f"Sharpe Ratio: {strat.analyzers.sharpe.get_analysis()['sharperatio']:.3f}")
print(f"Max Drawdown: {strat.analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")

# Plot
cerebro.plot()
```

**Advanced Strategy with Risk Management:**
```python
class RSIStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
        ('risk_per_trade', 0.02),  # 2% risk per trade
    )
    
    def __init__(self):
        self.rsi = bt.indicators.RSI(period=self.p.rsi_period)
        self.order = None
        
    def next(self):
        if self.order:
            return
            
        position_size = self.broker.getvalue() * self.p.risk_per_trade
        
        if self.rsi < self.p.rsi_oversold and not self.position:
            size = position_size / self.data.close[0]
            self.order = self.buy(size=size)
            
        elif self.rsi > self.p.rsi_overbought and self.position:
            self.order = self.sell(size=self.position.size)
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            else:
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
        self.order = None
```

**Pros:**
- Mature, well-documented
- Easy to learn
- Good for event-driven strategies

**Cons:**
- Slower than vectorized approaches
- Limited to single-machine execution
- Yahoo Finance data feed often broken

---

### 2.2 VectorBT

**Overview:** High-performance backtesting using vectorized operations and Numba acceleration.

**Key Features:**
- Vectorized backtesting (thousands of strategies in seconds)
- Numba-compiled operations
- Hyperparameter optimization
- Interactive Plotly visualizations
- Built-in data fetching (Yahoo Finance)
- Portfolio optimization (PRO version)

**Installation:**
```bash
pip install vectorbt
pip install "vectorbt[full]"  # All optional dependencies
```

**Basic Example:**
```python
import vectorbt as vbt
import numpy as np

# Download data
price = vbt.YFData.download('BTC-USD').get('Close')

# Simple buy and hold
pf = vbt.Portfolio.from_holding(price, init_cash=1000)
print(f"Total Profit: ${pf.total_profit():.2f}")
print(f"Total Return: {pf.total_return()*100:.2f}%")
```

**SMA Crossover Strategy:**
```python
# Calculate moving averages
fast_ma = vbt.MA.run(price, 10)
slow_ma = vbt.MA.run(price, 50)

# Generate signals
entries = fast_ma.ma_crossed_above(slow_ma)
exits = fast_ma.ma_crossed_below(slow_ma)

# Create portfolio
pf = vbt.Portfolio.from_signals(
    price, 
    entries, 
    exits, 
    init_cash=1000,
    fees=0.001  # 0.1% fees
)

# Stats
print(pf.stats())
```

**Parameter Optimization (10,000 combinations):**
```python
# Define parameter ranges
windows = np.arange(2, 101)

# Run all combinations
fast_ma, slow_ma = vbt.MA.run_combs(
    price, 
    window=windows, 
    r=2,  # Combinations of 2
    short_names=['fast', 'slow']
)

entries = fast_ma.ma_crossed_above(slow_ma)
exits = fast_ma.ma_crossed_below(slow_ma)

pf = vbt.Portfolio.from_signals(
    price, 
    entries, 
    exits,
    size=np.inf,
    fees=0.001
)

# Get best performing combination
total_returns = pf.total_return()
best_idx = total_returns.idxmax()
print(f"Best combination: {best_idx}")
print(f"Best return: {total_returns[best_idx]*100:.2f}%")

# Heatmap
fig = pf.total_return().vbt.heatmap(
    x_level='fast_window',
    y_level='slow_window',
    symmetric=True
)
fig.show()
```

**Pros:**
- Extremely fast (vectorized + Numba)
- Excellent for parameter optimization
- Beautiful interactive plots
- Great for research and analysis

**Cons:**
- Steeper learning curve
- Less intuitive for event-driven logic
- Some features locked behind PRO ($29/mo)

---

### 2.3 QuantConnect (LEAN Engine)

**Overview:** Cloud-based algorithmic trading platform with open-source LEAN engine.

**Key Features:**
- Cloud backtesting with tick data
- Multiple asset classes (Equity, Forex, Crypto, Futures, Options)
- 400+ datasets
- Live trading to multiple brokers
- Alpha Streams marketplace

**Pricing:**
| Feature | Free | Researcher ($8/mo) | Team ($20/mo) |
|---------|------|-------------------|---------------|
| Backtests/day | 10 | 100 | 500 |
| Real-time data | Delayed | Real-time | Real-time |
| Node speed | 1x | 4x | 16x |
| Live trading | Yes | Yes | Yes |

**Installation (Local LEAN):**
```bash
docker pull quantconnect/lean:latest
```

**Basic Algorithm:**
```python
from AlgorithmImports import *

class BasicTemplateAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2023, 1, 1)
        self.SetCash(100000)
        
        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.SetBenchmark(self.symbol)
        
        # Simple moving average
        self.sma = self.SMA(self.symbol, 20, Resolution.Daily)
        self.SetWarmUp(20)
        
    def OnData(self, data):
        if self.IsWarmingUp:
            return
            
        if not self.Portfolio.Invested:
            if self.Securities[self.symbol].Price > self.sma.Current.Value:
                self.SetHoldings(self.symbol, 1.0)
        else:
            if self.Securities[self.symbol].Price < self.sma.Current.Value:
                self.Liquidate()
```

**Pros:**
- Professional-grade data
- Supports multiple brokers
- Active community
- Good for multi-asset strategies

**Cons:**
- Learning curve (custom API)
- Cloud dependency for full features
- Local setup requires Docker

---

### 2.4 Library Comparison

| Feature | Backtrader | VectorBT | QuantConnect |
|---------|------------|----------|--------------|
| Speed | Moderate | Very Fast | Moderate |
| Ease of Use | Easy | Moderate | Moderate |
| Live Trading | Yes | Limited | Yes |
| Parameter Optimization | Manual | Excellent | Built-in |
| Visualization | Matplotlib | Plotly | Built-in |
| Cost | Free | Free/PRO | Free/Paid |
| Best For | Beginners | Research | Production |

---

## 3. Free Data Sources for OHLCV Data

### 3.1 Yahoo Finance (yfinance)

**Overview:** Unofficial API for Yahoo Finance data.

**Features:**
- Free historical data
- Stocks, ETFs, Crypto, Forex
- Fundamental data
- Options chains

**Limitations:**
- Rate limited (personal use only)
- Not for commercial use
- Sometimes unreliable
- 15-minute delay on intraday

**Python Example:**
```python
import yfinance as yf

# Single ticker
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1y", interval="1d")
print(hist)

# Multiple tickers
data = yf.download(["SPY", "QQQ", "IWM"], period="1y")
print(data['Close'])

# Intraday (max 60 days)
intraday = yf.download("AAPL", period="5d", interval="5m")

# Fundamental data
info = ticker.info
print(f"PE Ratio: {info.get('trailingPE')}")
print(f"Market Cap: {info.get('marketCap')}")
```

---

### 3.2 Alpaca Market Data API

**Features:**
- 7+ years historical data
- Real-time streaming (paid)
- US equities and crypto
- Bar aggregation
- Corporate actions

**Pricing:**
- Free: 200 calls/min, 15-min delayed, 30 symbols
- Paid: $9-99/mo for real-time

---

### 3.3 Polygon.io

**Features:**
- US Stocks, Options, Forex, Crypto
- Tick-level historical data
- Real-time WebSocket streaming

**Pricing:**
- Free: 5 API calls/min, delayed data
- Starter: $49/mo
- Developer: $199/mo

---

### 3.4 CryptoCompare (Crypto Only)

**Features:**
- 9,000+ cryptocurrencies
- 700+ exchanges
- Historical OHLCV
- WebSocket streaming

**Pricing:**
- Free: 100k calls/month
- Paid: Starting at $79/mo

---

### 3.5 CCXT (Crypto Exchange Aggregator)

**Overview:** Unified API for 100+ crypto exchanges.

**Python Example:**
```python
import ccxt

# Connect to exchange
exchange = ccxt.binance()

# Fetch OHLCV
ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h', limit=100)

# Convert to DataFrame
import pandas as pd
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
```

---

### 3.6 Data Source Comparison

| Source | Asset Classes | Cost | Quality | Best For |
|--------|--------------|------|---------|----------|
| Yahoo Finance | Stocks, ETFs, Crypto, Forex | Free | Moderate | Personal research |
| Alpaca | US Stocks, Crypto | Free/Paid | High | Algo trading |
| Polygon.io | Stocks, Options, Forex, Crypto | Paid | Very High | Professional use |
| CryptoCompare | Crypto | Free/Paid | High | Crypto analysis |
| CCXT | Crypto (100+ exchanges) | Free | High | Multi-exchange arbitrage |

---

## 4. Execution Models

### 4.1 Order Types

#### Market Orders
Execute immediately at best available price.

```python
# Alpaca
api.submit_order(
    symbol='AAPL',
    qty=100,
    side='buy',
    type='market',
    time_in_force='day'
)

# IBKR (via ib_insync)
market_order = MarketOrder('BUY', 100)
trade = ib.placeOrder(contract, market_order)
```

**Pros:**
- Guaranteed execution
- Simple to use

**Cons:**
- Subject to slippage
- No price control

---

#### Limit Orders
Execute only at specified price or better.

```python
# Alpaca
api.submit_order(
    symbol='AAPL',
    qty=100,
    side='buy',
    type='limit',
    time_in_force='gtc',  # Good Till Canceled
    limit_price=150.00
)

# With bracket (take profit + stop loss)
api.submit_order(
    symbol='AAPL',
    qty=100,
    side='buy',
    type='limit',
    time_in_force='gtc',
    limit_price=150.00,
    order_class='bracket',
    take_profit=dict(limit_price=170.00),
    stop_loss=dict(stop_price=140.00)
)
```

**Pros:**
- Price control
- No slippage (for fills)
- Can be maker orders (lower fees on some exchanges)

**Cons:**
- No guaranteed execution
- May miss fast-moving opportunities

---

#### Stop Orders (Stop-Loss)
Convert to market order when stop price is hit.

```python
# Stop-loss order
api.submit_order(
    symbol='AAPL',
    qty=100,
    side='sell',
    type='stop',
    time_in_force='gtc',
    stop_price=140.00  # Triggers at $140
)

# Stop-limit order
api.submit_order(
    symbol='AAPL',
    qty=100,
    side='sell',
    type='stop_limit',
    time_in_force='gtc',
    stop_price=140.00,
    limit_price=139.50  # Won't sell below this
)
```

---

#### Time-in-Force (TIF) Options

| TIF | Description | Use Case |
|-----|-------------|----------|
| `day` | Expires at market close | Standard trading |
| `gtc` | Good till canceled | Long-term orders |
| `ioc` | Immediate or cancel | Fast execution needed |
| `fok` | Fill or kill | All or nothing |
| `opg` | At market open | Opening auction |
| `cls` | At market close | Closing auction |

---

### 4.2 Slippage

**Definition:** Difference between expected execution price and actual execution price.

**Types:**
- **Positive slippage:** Better price than expected
- **Negative slippage:** Worse price than expected

**Factors Affecting Slippage:**
1. Market volatility
2. Order size relative to liquidity
3. Time of day
4. Asset class (crypto > stocks > forex)

**Slippage Estimation Example (Backtrader):**
```python
# Fixed slippage
cerebro.broker.set_slippage_fixed(
    fixed=0.02,  # $0.02 per share
    slip_open=True,
    slip_limit=True,
    slip_match=True,
    slip_out=True
)

# Percentage slippage
cerebro.broker.set_slippage_perc(
    perc=0.001,  # 0.1%
    slip_open=True,
    slip_limit=False,  # No slippage on limit orders
    slip_match=True,
    slip_out=True
)
```

**Slippage Estimation Example (VectorBT):**
```python
pf = vbt.Portfolio.from_signals(
    price,
    entries,
    exits,
    slippage=0.001,  # 0.1% slippage per trade
    fees=0.001,
    freq='1D'
)
```

**Slippage Mitigation Strategies:**

1. **Use Limit Orders:**
   - Guarantees price (if filled)
   - No negative slippage

2. **Trade During High Liquidity:**
   - Market open/close
   - Avoid lunch hours (11:30am - 2:00pm ET)

3. **Split Large Orders:**
```python
# TWAP (Time-Weighted Average Price)
def twap_order(symbol, total_qty, num_slices=10, interval_sec=60):
    slice_qty = total_qty // num_slices
    for i in range(num_slices):
        api.submit_order(
            symbol=symbol,
            qty=slice_qty,
            side='buy',
            type='market',
            time_in_force='ioc'
        )
        time.sleep(interval_sec)
```

4. **Use Volume-Based Execution:**
```python
# VWAP (Volume-Weighted Average Price)
def vwap_execution(symbol, target_qty, participation_rate=0.1):
    """
    Execute at X% of volume to minimize market impact
    """
    executed = 0
    while executed < target_qty:
        # Get recent volume
        bar = api.get_barset(symbol, '1Min', limit=1)
        volume = bar[symbol][0].v
        
        # Calculate slice size
        slice_size = min(int(volume * participation_rate), target_qty - executed)
        
        if slice_size > 0:
            api.submit_order(
                symbol=symbol,
                qty=slice_size,
                side='buy',
                type='market'
            )
            executed += slice_size
        
        time.sleep(60)
```

5. **Avoid News Events:**
   - Check economic calendar
   - Pause trading around major announcements

---

### 4.3 Execution Best Practices

1. **Always Use Paper Trading First**
```python
# Alpaca paper URL
base_url = 'https://paper-api.alpaca.markets'

# IBKR paper account
ib.connect('127.0.0.1', 7497, clientId=1)  # Paper port
```

2. **Implement Position Sizing**
```python
def calculate_position_size(account_value, risk_per_trade, entry_price, stop_price):
    """
    Risk-based position sizing
    """
    risk_amount = account_value * risk_per_trade
    risk_per_share = abs(entry_price - stop_price)
    position_size = risk_amount / risk_per_share
    return int(position_size)

# Example
size = calculate_position_size(
    account_value=100000,
    risk_per_trade=0.02,  # 2%
    entry_price=150,
    stop_price=145
)
# Size = (100000 * 0.02) / (150 - 145) = 400 shares
```

3. **Monitor Fill Rates**
```python
def check_fill_quality(order, expected_price):
    slippage = abs(order.filled_avg_price - expected_price) / expected_price
    if slippage > 0.005:  # 0.5%
        print(f"WARNING: High slippage detected: {slippage*100:.2f}%")
```

4. **Handle Partial Fills**
```python
if order.status == 'partially_filled':
    filled_qty = order.filled_qty
    remaining_qty = order.qty - filled_qty
    print(f"Partial fill: {filled_qty}/{order.qty}")
```

---

## 5. Recommended Stack for Different Use Cases

### 5.1 Beginner (Free/Cheap)
- **Broker:** Alpaca (free commission, paper trading)
- **Library:** Backtrader (easy to learn)
- **Data:** Yahoo Finance + Alpaca
- **Cost:** $0

### 5.2 Intermediate Researcher
- **Broker:** Alpaca or IBKR
- **Library:** VectorBT (fast backtesting, optimization)
- **Data:** Alpaca Market Data ($9/mo for real-time)
- **Cost:** $9-20/mo

### 5.3 Professional/Production
- **Broker:** Interactive Brokers
- **Library:** QuantConnect LEAN or custom
- **Data:** Polygon.io or exchange direct
- **Cost:** $200+/mo

### 5.4 Crypto Specialist
- **Broker:** Binance
- **Library:** VectorBT or custom
- **Data:** CCXT + Binance API
- **Cost:** Trading fees only

---

## 6. Additional Resources

### Documentation Links
- Alpaca: https://docs.alpaca.markets/
- IBKR API: https://interactivebrokers.github.io/tws-api/
- Binance: https://binance-docs.github.io/apidocs/
- Backtrader: https://www.backtrader.com/docu/
- VectorBT: https://vectorbt.dev/

### Communities
- Alpaca Slack: https://alpaca.markets/slack
- QuantConnect Forums: https://www.quantconnect.com/forum
- r/algotrading: https://reddit.com/r/algotrading

---

## 7. Quick Start Template

```python
"""
Complete trading bot template using Alpaca + VectorBT
"""
import vectorbt as vbt
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
import pandas as pd

# Configuration
API_KEY = 'YOUR_API_KEY'
SECRET_KEY = 'YOUR_SECRET_KEY'
BASE_URL = 'https://paper-api.alpaca.markets'  # Paper trading

class TradingBot:
    def __init__(self):
        self.api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL)
        self.symbols = ['AAPL', 'MSFT', 'GOOGL']
        
    def get_historical_data(self, symbol, days=30):
        """Fetch historical data from Alpaca"""
        end = datetime.now()
        start = end - timedelta(days=days)
        
        bars = self.api.get_bars(
            symbol,
            timeframe='1Hour',
            start=start.isoformat(),
            end=end.isoformat()
        ).df
        
        return bars['close']
    
    def generate_signals(self, price):
        """Simple SMA crossover strategy"""
        fast_ma = vbt.MA.run(price, 10)
        slow_ma = vbt.MA.run(price, 30)
        
        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)
        
        return entries, exits
    
    def backtest(self, symbol):
        """Backtest strategy"""
        price = self.get_historical_data(symbol)
        entries, exits = self.generate_signals(price)
        
        pf = vbt.Portfolio.from_signals(
            price,
            entries,
            exits,
            init_cash=10000,
            fees=0.001,
            slippage=0.001
        )
        
        print(f"\n{symbol} Backtest Results:")
        print(pf.stats())
        return pf
    
    def run_live(self, symbol):
        """Execute live trade"""
        price = self.get_historical_data(symbol, days=5)
        entries, exits = self.generate_signals(price)
        
        # Get latest signal
        current_position = self.api.get_position(symbol).qty if self.api.list_positions() else 0
        
        if entries.iloc[-1] and float(current_position) == 0:
            # Buy signal
            self.api.submit_order(
                symbol=symbol,
                qty=10,
                side='buy',
                type='market',
                time_in_force='day'
            )
            print(f"BUY order placed for {symbol}")
            
        elif exits.iloc[-1] and float(current_position) > 0:
            # Sell signal
            self.api.submit_order(
                symbol=symbol,
                qty=current_position,
                side='sell',
                type='market',
                time_in_force='day'
            )
            print(f"SELL order placed for {symbol}")

if __name__ == '__main__':
    bot = TradingBot()
    
    # Backtest first
    for symbol in bot.symbols:
        bot.backtest(symbol)
    
    # Run live (comment out until ready)
    # bot.run_live('AAPL')
```

---

*Report generated: February 2026*
*Disclaimer: This report is for educational purposes. Trading involves risk. Always test strategies thoroughly before deploying live capital.*
