"""
Configuration file for the Risk-Adaptive Crypto Trading Alert Bot.

This file contains all configuration settings, API keys, and user preferences.
Users should fill in their own values for the placeholders below.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# =============================================================================
# TELEGRAM BOT CONFIGURATION
# =============================================================================
# Get Telegram bot token from environment variable or set directly
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN_HERE')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'YOUR_TELEGRAM_CHAT_ID_HERE')

# =============================================================================
# EXCHANGE CONFIGURATION
# =============================================================================
EXCHANGE_NAME = 'binance'
EXCHANGE_SANDBOX = False  # Set to True for testing with sandbox

# =============================================================================
# TRADING PAIRS AND ASSETS
# =============================================================================
# List of trading pairs to monitor
TRADING_PAIRS = [
    'BTC/USDT',
    'ETH/USDT',
    'BNB/USDT',
    'ADA/USDT',
    'SOL/USDT',
    
]

# Default trading pair for alerts (can be overridden)
DEFAULT_PAIR = 'BTC/USDT'

# =============================================================================
# RISK PROFILE SETTINGS
# =============================================================================
# Enable/disable specific risk profiles
ENABLED_PROFILES = {
    'aggressive_momentum_ignition': True,
    'moderate_ema_crossover': True,
    'conservative_trend_rider': True
}

# =============================================================================
# SCHEDULING CONFIGURATION
# =============================================================================
# Time intervals for each risk profile (in minutes)
SCHEDULE_INTERVALS = {
    'aggressive_momentum_ignition': 5,      # Check every 5 minutes
    'moderate_ema_crossover': 15,           # Check every 15 minutes
    'conservative_trend_rider': 240         # Check every 4 hours (4 * 60 minutes)
}

# =============================================================================
# ENHANCED STRATEGY PARAMETERS
# =============================================================================

# Aggressive Strategy - Momentum Ignition (OPTIMIZED)
AGGRESSIVE_MOMENTUM_IGNITION = {
    'timeframe': '5m',
    'description': 'Optimized high-frequency scalping with improved StochRSI and risk management',
    'parameters': {
        'stoch_rsi_k': 8,           # Reduced from 10 for faster signals
        'stoch_rsi_d': 2,           # Reduced from 3 for faster confirmation
        'rsi_length': 11,           # Kept same
        'oversold_threshold': 10,   # More extreme oversold (from 15)
        'overbought_threshold': 90, # More extreme overbought (from 85)
        'volume_multiplier': 2.0,   # Increased from 1.5 for stronger confirmation
        'max_hold_period': '15m',   # Kept same
        'position_size': 0.03,      # Kept same
        'leverage': 3               # Reduced from 5 for better risk management
    },
    'filters': {
        'volatility': 0.018,        # Reduced from 2.5% to 1.8% for tighter control
        'time_start': '09:30',      # Optimized trading hours (from 08:00)
        'time_end': '16:00',        # Optimized trading hours (from 20:00)
        'wick_confirmation': True,  # New: require wick confirmation
        'partial_exits': [0.5, 1.0, 1.5],  # New: partial profit taking
        'divergence_detection': True  # New: RSI divergence confirmation
    }
}

# Moderate Strategy - EMA Crossover (OPTIMIZED)
MODERATE_EMA_CROSSOVER = {
    'timeframe': '15m',
    'description': 'Optimized swing trading with improved EMA periods and divergence detection',
    'parameters': {
        'ema_fast': 8,              # Reduced from 12 for faster signals
        'ema_slow': 34,             # Increased from 26 for better trend confirmation
        'rsi_length': 14,           # Kept same
        'rsi_bullish': 40,          # More bullish threshold (from 45)
        'rsi_bearish': 60,          # More bearish threshold (from 55)
        'trend_ema': 50,            # Reduced from 100 for faster trend detection
        'position_size': 0.02,      # Kept same
        'leverage': 2               # Reduced from 3 for better risk management
    },
    'filters': {
        'session': '12:00-20:00',   # Extended trading session
        'min_candle_body': 0.005,   # New: minimum 0.5% candle body
        'divergence_detection': True, # New: RSI divergence detection
        'required_volume_spike': 1.8 # New: 1.8x volume requirement
    }
}

# Conservative Strategy - Trend Rider (4h) (OPTIMIZED)
CONSERVATIVE_TREND_RIDER = {
    'timeframe': '4h',
    'description': 'Optimized trend following with improved exit timing and position management',
    'parameters': {
        'ema_fast': 50,             # Kept same
        'ema_slow': 200,            # Kept same
        'adx_threshold': 25,        # Kept same
        'rsi_length': 14,           # Kept same
        'rsi_upper': 60,            # Kept same
        'rsi_lower': 40,            # Kept same
        'leverage': 1               # Reduced from 2 for ultra-conservative approach
    },
    'filters': {
        'min_hold_period': '24h',   # Reduced from 2 days for faster exits
        'max_hold_period': '72h',   # Reduced from 3 days for better capital efficiency
        'trailing_stop': True,      # New: dynamic trailing stop
        'profit_scaling': True      # New: partial profit taking
    },
    'exit_conditions': {
        'trailing_stop_multiplier': 2.5,  # 2.5x ATR for trailing stop
        'profit_scaling_levels': [
            {'threshold': 1.5, 'close_pct': 30},  # Close 30% at 1.5x risk
            {'threshold': 3.0, 'close_pct': 50}   # Close 50% at 3.0x risk
        ]
    }
}

# =============================================================================
# CAPITAL ALLOCATION AND RISK MANAGEMENT
# =============================================================================
CAPITAL_ALLOCATION = {
    'conservative_trend_rider': 0.5,    # 50% of capital
    'moderate_ema_crossover': 0.3,       # 30% of capital
    'aggressive_momentum_ignition': 0.2  # 20% of capital
}

EXECUTION_PRIORITY = [
    'conservative_trend_rider',
    'moderate_ema_crossover',
    'aggressive_momentum_ignition'
]

RISK_MANAGEMENT = {
    'daily_loss_limit': 0.05,           # 5% daily loss limit
    'max_position_overlap': 2,          # Max 2 overlapping positions
    'leverage_caps': {
        'aggressive_momentum_ignition': 5,    # Reduced from 100 for better risk control
        'moderate_ema_crossover': 3,          # Reduced from 25 for better risk control
        'conservative_trend_rider': 1         # Reduced from 2 for ultra-conservative
    },
    'position_sizing': {
        'max_risk_per_trade': 0.02,     # 2% max risk per trade
        'correlation_threshold': 0.7,    # Max correlation between positions
        'max_portfolio_risk': 0.15      # 15% max portfolio risk
    }
}

# =============================================================================
# BACKTESTING CONFIGURATION
# =============================================================================
BACKTEST_CONFIG = {
    'data_requirements': {
        'timeframes': ['5m', '15m', '4h', '1d'],
        'minimum_history': '2 years',
        'required_columns': ['open', 'high', 'low', 'close', 'volume']
    },
    'test_periods': {
        'training': '2020-2022',
        'validation': '2023',
        'testing': '2024'
    },
    'slippage_model': {
        'limit_orders': 0.0005,          # 0.05% slippage for limit orders
        'market_orders': 0.0015          # 0.15% slippage for market orders
    },
    'metrics': [
        'sharpe_ratio',
        'max_drawdown',
        'win_rate',
        'profit_factor',
        'strategy_correlation'
    ]
}

# =============================================================================
# ALERT CONFIGURATION
# =============================================================================
# Console Output Configuration
CONSOLE_ALERTS_ENABLED = True  # Always enabled for local monitoring

# Maximum number of alerts per day per strategy to prevent spam
MAX_ALERTS_PER_DAY = 10

# Alert cooldown period (in minutes) to prevent duplicate alerts
ALERT_COOLDOWN_MINUTES = 30

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = 'trading_bot.log'

# =============================================================================
# ERROR HANDLING
# =============================================================================
# Maximum number of retries for API calls
MAX_RETRIES = 3

# Delay between retries (in seconds)
RETRY_DELAY = 5

# =============================================================================
# DATA FETCHING SETTINGS
# =============================================================================
# Number of candles to fetch for analysis
CANDLE_LIMIT = 200

# Timeout for API requests (in seconds)
REQUEST_TIMEOUT = 30

# =============================================================================
# DEVELOPMENT AND TESTING
# =============================================================================
# Enable debug mode for additional logging
DEBUG_MODE = False

# Enable dry-run mode (no actual alerts sent)
DRY_RUN_MODE = True

# Enable test mode (runs without Telegram, uses console output)
TEST_MODE = False

# Skip Telegram initialization in test mode
SKIP_TELEGRAM_IN_TEST = False

# =============================================================================
# LEGACY PARAMETERS (for backward compatibility)
# =============================================================================
# These are kept for backward compatibility but should not be used
AGGRESSIVE_PARAMS = AGGRESSIVE_MOMENTUM_IGNITION['parameters']
MODERATE_PARAMS = MODERATE_EMA_CROSSOVER['parameters']
CONSERVATIVE_PARAMS = CONSERVATIVE_TREND_RIDER['parameters']
