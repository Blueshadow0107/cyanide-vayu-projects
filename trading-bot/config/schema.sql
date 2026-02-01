-- VAYU Trading Bot - SQLite Schema
-- State management for positions, trades, and P&L
-- Copy to ~/.vayu/ on setup

-- Current positions
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,  -- 'long' or 'short'
    entry_price REAL NOT NULL,
    size REAL NOT NULL,
    stop_price REAL NOT NULL,
    take_profit_price REAL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP,
    exit_price REAL,
    pnl_realized REAL,
    pnl_percent REAL,
    status TEXT DEFAULT 'open',  -- 'open', 'closed', 'liquidated'
    order_id TEXT,
    strategy_params TEXT  -- JSON of RSI, EMA values at entry
);

-- Trade history (completed trades)
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    entry_price REAL NOT NULL,
    exit_price REAL NOT NULL,
    size REAL NOT NULL,
    pnl_realized REAL NOT NULL,
    pnl_percent REAL NOT NULL,
    entry_time TIMESTAMP NOT NULL,
    exit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_hours REAL,
    exit_reason TEXT,  -- 'rsi_mean_reversion', 'stop_loss', 'take_profit', 'time_limit', 'manual_kill'
    max_drawdown_percent REAL,
    slippage_entry REAL,
    slippage_exit REAL,
    fees_paid REAL
);

-- Daily P&L tracking for circuit breaker
CREATE TABLE IF NOT EXISTS daily_pnl (
    date TEXT PRIMARY KEY,
    starting_equity REAL NOT NULL,
    ending_equity REAL,
    total_pnl REAL DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    max_drawdown_percent REAL DEFAULT 0,
    circuit_breaker_triggered BOOLEAN DEFAULT FALSE
);

-- System events (errors, kills, restarts)
CREATE TABLE IF NOT EXISTS system_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,  -- 'startup', 'kill_switch', 'circuit_breaker', 'error', 'stale_data', 'rate_limit'
    severity TEXT,  -- 'info', 'warning', 'critical'
    message TEXT,
    details TEXT  -- JSON additional data
);

-- Rate limiting tracking
CREATE TABLE IF NOT EXISTS api_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    endpoint TEXT NOT NULL,
    success BOOLEAN,
    error_message TEXT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status);
CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_date ON trades(exit_time);
CREATE INDEX IF NOT EXISTS idx_api_calls_timestamp ON api_calls(timestamp);
