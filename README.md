# 🚀 Risk-Adaptive Crypto Trading Alert Bot

A sophisticated, multi-strategy cryptocurrency trading alert bot that automatically monitors market conditions and sends real-time alerts via Telegram based on three distinct risk profiles: Aggressive, Moderate, and Conservative.

## ✨ Features

### 🎯 **Risk Profiles & Strategies**

1. **🚨 Aggressive Profile - Momentum Ignition**
   - Timeframe: 5 minutes
   - Strategy: Stochastic RSI bullish/bearish cross in oversold/overbought zones
   - Best for: Day traders and scalpers

2. **⚖️ Moderate Profile - Filtered EMA Crossover**
   - Timeframe: 15 minutes with 4-hour trend filter
   - Strategy: EMA crossover with RSI momentum confirmation and higher timeframe trend validation
   - Best for: Swing traders

3. **🛡️ Conservative Profile - Trend Rider**
   - Timeframe: 4 hours
   - Strategy: Golden Cross (50-day SMA above 200-day SMA) / Death Cross
   - Best for: Long-term position traders

### 🔧 **Key Features**

- **Stateful Alert Logic**: Prevents duplicate alerts using intelligent state tracking
- **Multi-Timeframe Analysis**: Combines data from different timeframes for confirmation
- **Real-Time Monitoring**: Continuous market surveillance with configurable intervals
- **Telegram Integration**: Instant notifications with rich formatting
- **Advanced Risk Management**: Position sizing, leverage caps, and portfolio risk controls
- **Comprehensive Backtesting**: Historical strategy validation with performance metrics
- **Error Handling**: Robust error handling with retry mechanisms
- **Logging**: Comprehensive logging for debugging and monitoring
- **Configurable**: Easy customization through `config.py`

## 📁 **Project Structure**

```
trade-alert/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── config.py                          # Configuration settings
├── enhanced_main.py                   # Main bot application
├── enhanced_strategy_engine.py        # Core strategy engine
├── data_handler.py                    # Data fetching and processing
├── telegram_bot.py                    # Telegram integration
├── enhanced_backtest_engine.py        # Backtesting engine
└── run_enhanced_backtest.py           # Backtesting runner
```

## 🚀 **Quick Start**

### 1. **Clone the Repository**
```bash
git clone <your-repo-url>
cd trade-alert
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Configure the Bot**
Create a `.env` file in the project root:
```bash
# .env
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
TELEGRAM_CHAT_ID=your_actual_chat_id_here
```

### 4. **Run the Bot**
```bash
# Start the main bot
python enhanced_main.py

# Or run backtesting
python run_enhanced_backtest.py
```

## 🔧 **Configuration**

### **Telegram Bot Setup**

1. **Create a Telegram Bot**:
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Use `/newbot` command
   - Follow instructions to create your bot
   - Copy the bot token

2. **Get Your Chat ID**:
   - Message your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Look for the `chat.id` field in the response

### **Trading Pairs**
Edit `config.py` to customize which trading pairs to monitor:
```python
TRADING_PAIRS = [
    'BTC/USDT',
    'ETH/USDT',
    'BNB/USDT',
    'ADA/USDT',
    'SOL/USDT'
]
```

### **Risk Profile Settings**
Enable/disable specific risk profiles in `config.py`:
```python
ENABLED_PROFILES = {
    'aggressive_momentum_ignition': True,    # Check every 5 minutes
    'moderate_ema_crossover': True,          # Check every 15 minutes
    'conservative_trend_rider': True         # Check every 4 hours
}
```

## 📊 **Alert Examples**

### **Aggressive Strategy Alert**
```
🚨 TRADING ALERT 🚨

Profile: Aggressive
Strategy: Momentum Ignition
Signal: LONG
Symbol: BTC/USDT
Timeframe: 5m
Price: $45,250.00
Time: 2024-01-01 12:00:00 UTC
```

### **Moderate Strategy Alert**
```
⚖️ TRADING ALERT ⚖️

Profile: Moderate
Strategy: Filtered EMA Crossover
Signal: SHORT
Symbol: ETH/USDT
Timeframe: 15m
Price: $2,850.00
Time: 2024-01-01 12:15:00 UTC
```

## 🧪 **Testing & Development**

### **Test Mode**
The bot includes a test mode that runs without Telegram:
```python
# In config.py
TEST_MODE = True
SKIP_TELEGRAM_IN_TEST = True
```

### **Backtesting**
Run comprehensive backtests on historical data:
```bash
python run_enhanced_backtest.py
```

## 📈 **Performance & Metrics**

The bot tracks comprehensive performance metrics:
- **Strategy Performance**: Win rate, profit factor, Sharpe ratio
- **Risk Metrics**: Maximum drawdown, position sizing, leverage usage
- **Portfolio Analysis**: Strategy correlations, capital allocation
- **Real-time Monitoring**: Bot health, error tracking, uptime

## 🔒 **Security & Best Practices**

- **API Keys**: Never commit API keys to version control
- **Environment Variables**: Use `.env` files for sensitive data
- **Network Security**: Ensure secure network connections
- **Access Control**: Limit bot access to trusted users only

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License.

## ⚠️ **Disclaimer**

This software is for **educational and informational purposes only**. It is not financial advice. Cryptocurrency trading involves substantial risk and may result in the loss of your invested capital. Always do your own research and consider consulting with a financial advisor before making investment decisions.

## 🆘 **Support**

For support and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Open an issue on GitHub

---

**Happy Trading! 🚀📈**
