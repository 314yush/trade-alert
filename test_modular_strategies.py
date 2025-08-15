#!/usr/bin/env python3
"""
Test Script for Modular Strategy System

This script demonstrates how easy it is to:
1. Modify individual strategies
2. Add new strategies
3. Test strategies independently
4. Update parameters on the fly
"""

import logging
from datetime import datetime
from strategy_manager import StrategyManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_strategy_modification():
    """Test modifying strategy parameters on the fly."""
    print("🔧 TESTING STRATEGY MODIFICATION")
    print("=" * 50)
    
    # Initialize strategy manager
    manager = StrategyManager()
    
    # Get current parameters for aggressive strategy
    current_params = manager.get_strategy_parameters('aggressive_momentum_ignition')
    print(f"Current aggressive strategy parameters:")
    print(f"  Oversold threshold: {current_params['parameters']['oversold_threshold']}")
    print(f"  Volume multiplier: {current_params['parameters']['volume_multiplier']}")
    
    # Modify parameters
    new_params = {
        'parameters': {
            'oversold_threshold': 15,  # Change from default to 15
            'volume_multiplier': 2.5   # Increase volume requirement
        }
    }
    
    success = manager.update_strategy_parameters('aggressive_momentum_ignition', new_params)
    if success:
        print("✅ Parameters updated successfully!")
        
        # Verify the change
        updated_params = manager.get_strategy_parameters('aggressive_momentum_ignition')
        print(f"Updated oversold threshold: {updated_params['parameters']['oversold_threshold']}")
        print(f"Updated volume multiplier: {updated_params['parameters']['volume_multiplier']}")
    else:
        print("❌ Failed to update parameters")
    
    print()


def test_strategy_enabling_disabling():
    """Test enabling and disabling strategies."""
    print("🔄 TESTING STRATEGY ENABLING/DISABLING")
    print("=" * 50)
    
    manager = StrategyManager()
    
    # Get initial status
    status = manager.get_strategy_status()
    print("Initial strategy status:")
    for name, info in status.items():
        print(f"  {name}: {'ENABLED' if info['enabled'] else 'DISABLED'}")
    
    # Disable aggressive strategy
    print("\nDisabling aggressive strategy...")
    manager.disable_strategy('aggressive_momentum_ignition')
    
    # Re-enable it
    print("Re-enabling aggressive strategy...")
    manager.enable_strategy('aggressive_momentum_ignition')
    
    # Check final status
    final_status = manager.get_strategy_status()
    print("\nFinal strategy status:")
    for name, info in final_status.items():
        print(f"  {name}: {'ENABLED' if info['enabled'] else 'DISABLED'}")
    
    print()


def test_individual_strategy_checking():
    """Test checking individual strategies."""
    print("🔍 TESTING INDIVIDUAL STRATEGY CHECKING")
    print("=" * 50)
    
    manager = StrategyManager()
    
    # Test each strategy individually
    strategies = ['aggressive_momentum_ignition', 'moderate_ema_crossover', 'conservative_trend_rider']
    
    for strategy_name in strategies:
        print(f"\nTesting {strategy_name}...")
        try:
            signal = manager.check_strategy(strategy_name, 'BTC/USDT')
            if signal:
                print(f"  ✅ Signal generated: {signal['signal_type']} {signal['symbol']}")
            else:
                print(f"  ⚠️  No signal generated")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print()


def test_strategy_statistics():
    """Test strategy statistics and monitoring."""
    print("📊 TESTING STRATEGY STATISTICS")
    print("=" * 50)
    
    manager = StrategyManager()
    
    # Get statistics for all strategies
    status = manager.get_strategy_status()
    
    for name, info in status.items():
        print(f"\n{name}:")
        print(f"  Timeframe: {info['timeframe']}")
        print(f"  Interval: {info['interval']} minutes")
        print(f"  Enabled: {info['enabled']}")
        print(f"  Signals Generated: {info['statistics']['signals_generated']}")
        print(f"  Last Signal: {info['statistics']['last_signal_time']}")
    
    print()


def test_adding_custom_strategy():
    """Test adding a custom strategy dynamically."""
    print("➕ TESTING CUSTOM STRATEGY ADDITION")
    print("=" * 50)
    
    from strategies.base_strategy import BaseStrategy
    
    # Create a custom strategy
    class CustomTestStrategy(BaseStrategy):
        def __init__(self):
            super().__init__("Custom Test", "1h", "Test strategy for demonstration")
            self.params = {'test_param': 42}
        
        def check_signal(self, symbol, data):
            # Always return a test signal
            return self.format_signal(
                'long', symbol, 50000, 49000, 52000,
                custom_param=self.params['test_param']
            )
        
        def get_parameters(self):
            return {'custom': True, 'params': self.params}
    
    manager = StrategyManager()
    
    # Add the custom strategy
    custom_config = {
        'timeframe': '1h',
        'interval': 60,
        'enabled': True
    }
    
    success = manager.add_strategy('custom_test', CustomTestStrategy(), custom_config)
    if success:
        print("✅ Custom strategy added successfully!")
        
        # Test it
        signal = manager.check_strategy('custom_test', 'ETH/USDT')
        if signal:
            print(f"  ✅ Custom strategy generated signal: {signal}")
        
        # Remove it
        manager.remove_strategy('custom_test')
        print("  ✅ Custom strategy removed successfully!")
    else:
        print("❌ Failed to add custom strategy")
    
    print()


def main():
    """Run all tests."""
    print("🚀 MODULAR STRATEGY SYSTEM TEST")
    print("=" * 60)
    print(f"Testing started at: {datetime.now()}")
    print()
    
    try:
        # Run all tests
        test_strategy_modification()
        test_strategy_enabling_disabling()
        test_individual_strategy_checking()
        test_strategy_statistics()
        test_adding_custom_strategy()
        
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logger.error(f"Test failed: {e}")
    
    finally:
        # Cleanup
        try:
            manager = StrategyManager()
            manager.cleanup()
            print("🧹 Cleanup completed")
        except:
            pass


if __name__ == "__main__":
    main()
