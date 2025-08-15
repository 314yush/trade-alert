#!/usr/bin/env python3
"""
Debug Script: Why No Trading Signals?

This script will help diagnose why your strategies aren't generating signals.
"""

import logging
from datetime import datetime
from strategy_manager import StrategyManager
from data_handler import DataHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_market_data():
    """Test if market data is being fetched correctly."""
    print("🔍 TESTING MARKET DATA")
    print("=" * 50)
    
    data_handler = DataHandler()
    
    # Test different timeframes
    timeframes = ['5m', '15m', '4h']
    symbols = ['BTC/USDT', 'ETH/USDT']
    
    for symbol in symbols:
        print(f"\n📊 Testing {symbol}:")
        for timeframe in timeframes:
            try:
                data = data_handler.fetch_ohlcv(symbol, timeframe, 100)
                if data is not None and not data.empty:
                    print(f"  ✅ {timeframe}: {len(data)} candles, Latest: ${data['close'].iloc[-1]:,.2f}")
                    
                    # Check if data is recent
                    latest_time = data.index[-1]
                    print(f"      Latest candle: {latest_time}")
                    
                    # Check for recent price movement
                    price_change = ((data['close'].iloc[-1] - data['close'].iloc[-5]) / data['close'].iloc[-5]) * 100
                    print(f"      Price change (last 5 candles): {price_change:.2f}%")
                    
                else:
                    print(f"  ❌ {timeframe}: No data")
            except Exception as e:
                print(f"  ❌ {timeframe}: Error - {e}")
    
    print()


def test_strategy_parameters():
    """Test current strategy parameters."""
    print("⚙️ TESTING STRATEGY PARAMETERS")
    print("=" * 50)
    
    manager = StrategyManager()
    
    strategies = ['aggressive_momentum_ignition', 'moderate_ema_crossover', 'conservative_trend_rider']
    
    for strategy_name in strategies:
        print(f"\n🔧 {strategy_name}:")
        try:
            params = manager.get_strategy_parameters(strategy_name)
            if params:
                print(f"  Parameters: {params['parameters']}")
                print(f"  Filters: {params['filters']}")
                print(f"  Required columns: {params['required_columns']}")
            else:
                print(f"  ❌ No parameters found")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print()


def test_strategy_logic():
    """Test if strategies can generate signals with current data."""
    print("🧪 TESTING STRATEGY LOGIC")
    print("=" * 50)
    
    manager = StrategyManager()
    
    # Test with BTC/USDT
    symbol = 'BTC/USDT'
    print(f"Testing strategies with {symbol}")
    
    strategies = ['aggressive_momentum_ignition', 'moderate_ema_crossover', 'conservative_trend_rider']
    
    for strategy_name in strategies:
        print(f"\n🔍 Testing {strategy_name}...")
        try:
            # Check if strategy is enabled
            status = manager.get_strategy_status()
            if status[strategy_name]['enabled']:
                print(f"  ✅ Strategy is enabled")
                
                # Try to generate a signal
                signal = manager.check_strategy(strategy_name, symbol)
                if signal:
                    print(f"  🎯 SIGNAL GENERATED: {signal['signal_type']} {signal['symbol']}")
                    print(f"      Entry: ${signal['price']:,.2f}")
                    print(f"      Stop Loss: ${signal['stop_loss']:,.2f}")
                    print(f"      Take Profit: ${signal['take_profit']:,.2f}")
                else:
                    print(f"  ⚠️  No signal generated")
                    
                    # Get strategy statistics
                    stats = status[strategy_name]['statistics']
                    print(f"      Signals generated so far: {stats['signals_generated']}")
                    print(f"      Last signal time: {stats['last_signal_time']}")
            else:
                print(f"  ❌ Strategy is disabled")
                
        except Exception as e:
            print(f"  ❌ Error testing strategy: {e}")
    
    print()


def test_market_conditions():
    """Analyze current market conditions."""
    print("📈 ANALYZING MARKET CONDITIONS")
    print("=" * 50)
    
    data_handler = DataHandler()
    
    # Get recent data for analysis
    symbol = 'BTC/USDT'
    timeframe = '5m'
    
    try:
        data = data_handler.fetch_ohlcv(symbol, timeframe, 100)
        if data is not None and not data.empty:
            print(f"📊 {symbol} - {timeframe} Analysis:")
            
            # Calculate basic metrics
            current_price = data['close'].iloc[-1]
            price_24h_ago = data['close'].iloc[-288] if len(data) >= 288 else data['close'].iloc[0]
            
            # 24h change
            change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
            
            # Volatility (last 20 candles)
            recent_data = data.tail(20)
            volatility = (recent_data['high'].max() - recent_data['low'].min()) / recent_data['close'].mean() * 100
            
            # Volume analysis
            avg_volume = data['volume'].tail(20).mean()
            current_volume = data['volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume
            
            print(f"  Current Price: ${current_price:,.2f}")
            print(f"  24h Change: {change_24h:.2f}%")
            print(f"  Volatility (20 candles): {volatility:.2f}%")
            print(f"  Volume Ratio: {volume_ratio:.2f}x average")
            
            # Market condition assessment
            if abs(change_24h) < 1:
                print(f"  📊 Market: Sideways/Low volatility")
            elif change_24h > 3:
                print(f"  🚀 Market: Strong uptrend")
            elif change_24h < -3:
                print(f"  📉 Market: Strong downtrend")
            else:
                print(f"  ⚖️ Market: Moderate movement")
                
            if volume_ratio < 0.8:
                print(f"  📉 Volume: Below average (may reduce signals)")
            elif volume_ratio > 1.5:
                print(f"  📈 Volume: Above average (good for signals)")
            else:
                print(f"  ⚖️ Volume: Normal")
                
        else:
            print(f"❌ Could not fetch data for analysis")
            
    except Exception as e:
        print(f"❌ Error analyzing market: {e}")
    
    print()


def main():
    """Run all diagnostic tests."""
    print("🚀 SIGNAL DIAGNOSTIC TOOL")
    print("=" * 60)
    print(f"Testing started at: {datetime.now()}")
    print()
    
    try:
        # Run all tests
        test_market_data()
        test_strategy_parameters()
        test_strategy_logic()
        test_market_conditions()
        
        print("🎯 DIAGNOSTIC COMPLETE!")
        print("=" * 60)
        print("💡 TIPS TO GENERATE MORE SIGNALS:")
        print("1. Check if market conditions are suitable")
        print("2. Consider relaxing strategy parameters")
        print("3. Test with more volatile trading pairs")
        print("4. Verify data quality and timestamps")
        print("5. Check strategy enable/disable status")
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        logger.error(f"Diagnostic failed: {e}")
    
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
