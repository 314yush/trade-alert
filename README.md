# 🚀 Risk-Adaptive Crypto Trading Alert Bot

A sophisticated, **modular** cryptocurrency trading alert bot that automatically monitors market conditions and provides real-time alerts through a clean, console-based interface. Features three distinct risk profiles with a **modular architecture** that allows easy strategy modification and optimization.

## ✨ **Enhanced Features**

### 🎯 **Risk Profiles & Strategies**

1. **🚨 Aggressive Profile - Momentum Ignition**
   - Timeframe: 5 minutes
   - Strategy: Stochastic RSI bullish/bearish cross in oversold/overbought zones
   - Best for: Day traders and scalpers
   - **Modular**: Easy to modify parameters independently

2. **⚖️ Moderate Profile - EMA Crossover**
   - Timeframe: 15 minutes with 4-hour trend filter
   - Strategy: EMA crossover with RSI momentum confirmation and higher timeframe trend validation
   - Best for: Swing traders
   - **Modular**: Customizable filters and thresholds

3. **🛡️ Conservative Profile - Trend Rider**
   - Timeframe: 4 hours
   - Strategy: Golden Cross (50-day SMA above 200-day SMA) / Death Cross
   - Best for: Long-term position traders
   - **Modular**: Adjustable trend strength requirements

### 🔧 **Key Features**

- **🏗️ Modular Strategy Architecture**: Each strategy is a separate, modifiable class
- **⚡ Real-Time Parameter Updates**: Modify strategy parameters without restarting
- **🔄 Dynamic Strategy Management**: Enable/disable strategies on the fly
- **📊 Individual Strategy Monitoring**: Track performance of each strategy separately
- **💻 Console-Only Interface**: Clean, dependency-free operation
- **⏰ Minute-by-Minute Status Updates**: Real-time bot monitoring during testing
- **🔒 Dry Run Mode**: Safe testing without real trades
- **📈 Strategy Performance Tracking**: Monitor signals, errors, and uptime
- **🧪 Easy Testing Framework**: Test strategies independently

## 📁 **New Project Structure**

```
trade-alert/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── config.py                          # Configuration settings
├── enhanced_main.py                   # Main bot application (updated)
├── strategy_manager.py                # 🆕 Strategy coordination system
├── strategies/                        # 🆕 Modular strategy package
│   ├── __init__.py                   # Strategy package initialization
│   ├── base_strategy.py              # 🆕 Abstract base strategy class
│   ├── aggressive_momentum.py        # 🆕 Aggressive strategy (modular)
│   ├── moderate_ema.py               # 🆕 Moderate strategy (modular)
│   └── conservative_trend.py         # 🆕 Conservative strategy (modular)
├── data_handler.py                    # Data fetching and processing
├── enhanced_backtest_engine.py        # Backtesting engine
├── test_modular_strategies.py         # 🆕 Strategy testing framework
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

### 3. **Run the Bot**
```bash
# Start the main bot (console-only mode)
python3 enhanced_main.py

# Test the modular strategy system
python3 test_modular_strategies.py
```

## 🔧 **Modular Strategy System**

### **🎯 Easy Strategy Modification**

```python
from strategy_manager import StrategyManager

# Initialize manager
manager = StrategyManager()

# Modify aggressive strategy parameters
manager.update_strategy_parameters('aggressive_momentum_ignition', {
    'parameters': {
        'oversold_threshold': 15,      # Change from 10 to 15
        'volume_multiplier': 2.5       # Increase volume requirement
    }
})
```

### **➕ Add New Strategies**

```python
from strategies.base_strategy import BaseStrategy

# Create your own strategy
class MyCustomStrategy(BaseStrategy):
    def check_signal(self, symbol, data):
        # Your custom logic here
        pass

# Add it dynamically
manager.add_strategy('my_custom', MyCustomStrategy(), {
    'timeframe': '1h',
    'interval': 60,
    'enabled': True
})
```

### **🔄 Enable/Disable Strategies**

```python
# Disable a strategy temporarily
manager.disable_strategy('aggressive_momentum_ignition')

# Re-enable when ready
manager.enable_strategy('aggressive_momentum_ignition')
```

### **📊 Monitor Individual Performance**

```python
# Get statistics for each strategy
status = manager.get_strategy_status()
for name, info in status.items():
    print(f"{name}: {info['statistics']['signals_generated']} signals")
```

## 🎯 **Optimization Benefits**

### **🔧 Independent Strategy Development**
- Modify one strategy without affecting others
- Test different parameter combinations easily
- A/B test strategy variants
- Hot-reload parameter changes

### **📈 Performance Tracking**
- Monitor each strategy's success rate
- Track signal generation frequency
- Analyze strategy correlations
- Optimize based on real-time data

### **🧪 Testing & Validation**
- Test strategies independently
- Validate parameter changes quickly
- Compare strategy performance
- Systematic optimization workflow

## 📊 **Console Output Examples**

### **Bot Startup**
```
============================================================
🚀 ENHANCED TRADING BOT STARTED
The bot is now running with enhanced strategies:
• 🚨 Aggressive Momentum Ignition (5m)
• ⚖️ Moderate EMA Crossover (15m)
• 🛡️ Conservative Trend Rider (4h)

💻 CONSOLE ALERTS: ENABLED
⏰ MINUTE STATUS UPDATES: ACTIVE (for testing)
🔒 DRY RUN MODE: ENABLED (safe testing)
============================================================
```

### **Minute Status Updates**
```
============================================================
⏰ MINUTE STATUS UPDATE
Status: 🟢 RUNNING
Uptime: 0:15:00
Total Signals: 0
Errors: 0
Last Signal: None
Active Jobs: 6
Time: 00:50:03 UTC
============================================================
```

### **Trading Signals**
```
🚨 TRADING SIGNAL 🟢
Action: LONG
Asset: BTC/USDT
Strategy: Aggressive Momentum Ignition
Risk Level: HIGH RISK
Timeframe: 5m

Entry: $45,250.00
Stop Loss: $44,888.00
Take Profit: $45,928.00

Time: 12:00 UTC
```

## 🧪 **Testing & Development**

### **Test the Modular System**
```bash
# Run comprehensive strategy tests
python3 test_modular_strategies.py
```

This will test:
- ✅ Strategy parameter modification
- ✅ Strategy enabling/disabling
- ✅ Individual strategy checking
- ✅ Strategy statistics
- ✅ Custom strategy addition

### **Strategy Development Workflow**
1. **Modify Strategy**: Edit individual strategy files
2. **Test Changes**: Use the testing framework
3. **Validate**: Check performance metrics
4. **Optimize**: Iterate based on results
5. **Deploy**: Update parameters on the fly

## 🔧 **Configuration**

### **Strategy Parameters**
Each strategy has its own configuration section in `config.py`:

```python
AGGRESSIVE_MOMENTUM_IGNITION = {
    'parameters': {
        'oversold_threshold': 10,
        'volume_multiplier': 2.0,
        'leverage': 3,
        'max_hold_period': 30
    },
    'filters': {
        'divergence_detection': True,
        'partial_exits': [0.5, 0.8]
    }
}
```

### **Trading Pairs**
```python
TRADING_PAIRS = [
    'BTC/USDT',
    'ETH/USDT', 
    'BNB/USDT',
    'ADA/USDT',
    'SOL/USDT'
]
```

## 📈 **Performance & Metrics**

The bot now tracks comprehensive performance metrics:
- **Individual Strategy Performance**: Win rate, signal frequency, error tracking
- **Real-time Monitoring**: Bot health, uptime, active jobs
- **Strategy Statistics**: Signals generated, last signal time, performance history
- **Modular Analytics**: Compare strategies, track optimizations

## 🔒 **Security & Best Practices**

- **No External Dependencies**: Console-only operation for maximum security
- **Dry Run Mode**: Test strategies safely without real trades
- **Modular Architecture**: Isolated strategy testing and validation
- **Comprehensive Logging**: Track all operations and errors

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. **Modify individual strategies** without affecting others
4. Test your changes with the testing framework
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License.

## ⚠️ **Disclaimer**

This software is for **educational and informational purposes only**. It is not financial advice. Cryptocurrency trading involves substantial risk and may result in the loss of your invested capital. Always do your own research and consider consulting with a financial advisor before making investment decisions.

## 🆘 **Support**

For support and questions:
1. Check the testing framework: `python3 test_modular_strategies.py`
2. Review the logs for error details
3. Test individual strategies independently
4. Open an issue on GitHub

---

**Happy Trading & Optimizing! 🚀📈🔧**
