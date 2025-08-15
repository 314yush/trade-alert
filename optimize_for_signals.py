#!/usr/bin/env python3
"""
Strategy Optimization for Signal Generation

This script will make your strategies more sensitive to generate more signals
during low volatility periods.
"""

from strategy_manager import StrategyManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def optimize_aggressive_strategy():
    """Make aggressive strategy more sensitive."""
    print("🚨 OPTIMIZING AGGRESSIVE STRATEGY")
    print("=" * 50)
    
    manager = StrategyManager()
    
    # More sensitive parameters
    new_params = {
        'parameters': {
            'oversold_threshold': 25,      # Was 10 - now more sensitive
            'overbought_threshold': 75,    # Was 90 - now more sensitive
            'volume_multiplier': 1.2,      # Was 2.0 - now easier to meet
        },
        'filters': {
            'volatility': 0.005,           # Was 0.018 - lower threshold
        }
    }
    
    success = manager.update_strategy_parameters('aggressive_momentum_ignition', new_params)
    if success:
        print("✅ Aggressive strategy optimized!")
        print("   - Oversold threshold: 10 → 25")
        print("   - Overbought threshold: 90 → 75")
        print("   - Volume requirement: 2.0x → 1.2x")
        print("   - Volatility threshold: 1.8% → 0.5%")
    else:
        print("❌ Failed to optimize aggressive strategy")
    
    print()


def optimize_moderate_strategy():
    """Make moderate strategy more sensitive."""
    print("⚖️ OPTIMIZING MODERATE STRATEGY")
    print("=" * 50)
    
    manager = StrategyManager()
    
    # More sensitive parameters
    new_params = {
        'parameters': {
            'rsi_bullish': 35,            # Was 40 - easier bullish signal
            'rsi_bearish': 65,            # Was 60 - easier bearish signal
        },
        'filters': {
            'required_volume_spike': 1.2, # Was 1.8 - lower volume requirement
            'min_candle_body': 0.003,     # Was 0.005 - smaller candles OK
        }
    }
    
    success = manager.update_strategy_parameters('moderate_ema_crossover', new_params)
    if success:
        print("✅ Moderate strategy optimized!")
        print("   - RSI bullish threshold: 40 → 35")
        print("   - RSI bearish threshold: 60 → 65")
        print("   - Volume requirement: 1.8x → 1.2x")
        print("   - Min candle body: 0.5% → 0.3%")
    else:
        print("❌ Failed to optimize moderate strategy")
    
    print()


def optimize_conservative_strategy():
    """Make conservative strategy more sensitive."""
    print("🛡️ OPTIMIZING CONSERVATIVE STRATEGY")
    print("=" * 50)
    
    manager = StrategyManager()
    
    # More sensitive parameters
    new_params = {
        'parameters': {
            'adx_threshold': 15,          # Was 25 - weaker trends OK
            'rsi_upper': 65,              # Was 60 - easier bullish
            'rsi_lower': 35,              # Was 40 - easier bearish
        }
    }
    
    success = manager.update_strategy_parameters('conservative_trend_rider', new_params)
    if success:
        print("✅ Conservative strategy optimized!")
        print("   - ADX threshold: 25 → 15 (weaker trends OK)")
        print("   - RSI upper: 60 → 65 (easier bullish)")
        print("   - RSI lower: 40 → 35 (easier bearish)")
    else:
        print("❌ Failed to optimize conservative strategy")
    
    print()


def test_optimized_strategies():
    """Test if optimized strategies generate signals."""
    print("🧪 TESTING OPTIMIZED STRATEGIES")
    print("=" * 50)
    
    manager = StrategyManager()
    
    # Test with BTC/USDT
    symbol = 'BTC/USDT'
    print(f"Testing optimized strategies with {symbol}")
    
    strategies = ['aggressive_momentum_ignition', 'moderate_ema_crossover', 'conservative_trend_rider']
    
    for strategy_name in strategies:
        print(f"\n🔍 Testing {strategy_name}...")
        try:
            signal = manager.check_strategy(strategy_name, symbol)
            if signal:
                print(f"  🎯 SIGNAL GENERATED: {signal['signal_type']} {signal['symbol']}")
                print(f"      Entry: ${signal['price']:,.2f}")
                print(f"      Stop Loss: ${signal['stop_loss']:,.2f}")
                print(f"      Take Profit: ${signal['take_profit']:,.2f}")
            else:
                print(f"  ⚠️  Still no signal (market may be too calm)")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print()


def main():
    """Run strategy optimization."""
    print("🚀 STRATEGY OPTIMIZATION FOR SIGNAL GENERATION")
    print("=" * 60)
    
    try:
        # Optimize all strategies
        optimize_aggressive_strategy()
        optimize_moderate_strategy()
        optimize_conservative_strategy()
        
        print("🎯 OPTIMIZATION COMPLETE!")
        print("=" * 60)
        print("💡 What was optimized:")
        print("1. 🚨 Aggressive: Lower thresholds, easier volume")
        print("2. ⚖️ Moderate: Easier RSI conditions, lower volume")
        print("3. 🛡️ Conservative: Weaker trend requirements")
        print()
        print("🧪 Testing optimized strategies...")
        
        # Test the optimized strategies
        test_optimized_strategies()
        
        print("🎉 Ready to test with your main bot!")
        print("Run: python3 enhanced_main.py")
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        logger.error(f"Optimization failed: {e}")
    
    finally:
        # Cleanup
        try:
            manager = StrategyManager()
            manager.cleanup()
            print("\n🧹 Cleanup completed")
        except:
            pass


if __name__ == "__main__":
    main()
