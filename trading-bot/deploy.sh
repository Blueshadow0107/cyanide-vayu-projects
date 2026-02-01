#!/bin/bash
# Deploy VAYU Trading Bot
# ======================
# Automated deployment script for paper trading mode

set -e

echo "🌀 VAYU Trading Bot Deployment"
echo "=============================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Check for config
if [ ! -f "config/config.paper.yaml" ]; then
    echo "⚠️  Paper trading config not found. Copying template..."
    cp config/config.yaml.template config/config.paper.yaml
fi

# Create necessary directories
mkdir -p logs data

# Run validation tests
echo "🧪 Running validation tests..."
python3 -c "
import sys
sys.path.insert(0, '.')
from src.strategy.rsi_momentum import RSIMomentumStrategy
from src.strategy.risk_engine import RiskEngine
print('✓ Strategy modules import successfully')
"

# Check Kraken connection (sandbox)
echo "🔌 Testing Kraken sandbox connection..."
python3 -c "
import sys
import os
sys.path.insert(0, '.')
from src.exchange.kraken_client import KrakenClient
client = KrakenClient(sandbox=True)
print('✓ Kraken client initialized')
"

echo ""
echo "✅ Deployment validation complete!"
echo ""
echo "To start paper trading:"
echo "  python3 main.py --paper"
echo ""
echo "To run backtest:"
echo "  python3 -m src.backtest.backtest_engine"
echo ""
echo "To view performance:"
echo "  python3 -c 'from src.utils.performance import create_tracker; create_tracker().print_dashboard()'"
