#!/usr/bin/env python3
"""
Test script for Telegram integration with the trading bot.

This script tests the complete Telegram integration without running the full bot.
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_telegram_bot():
    """Test the Telegram bot functionality."""
    print("🧪 Testing Telegram Bot Integration")
    print("=" * 50)
    
    try:
        # Test 1: Import Telegram bot
        print("1. Testing Telegram bot import...")
        from telegram_bot import TelegramBot
        print("   ✅ Telegram bot imported successfully")
        
        # Test 2: Initialize bot
        print("2. Testing bot initialization...")
        bot = TelegramBot()
        if bot.is_initialized:
            print("   ✅ Bot initialized successfully")
        else:
            print("   ❌ Bot initialization failed")
            return False
        
        # Test 3: Test connection
        print("3. Testing Telegram connection...")
        if bot.test_connection():
            print("   ✅ Connection test successful")
        else:
            print("   ❌ Connection test failed")
            return False
        
        # Test 4: Test message formatting
        print("4. Testing message formatting...")
        
        # Test trading signal
        test_signal = {
            'signal_type': 'long',
            'symbol': 'BTC/USDT',
            'profile': 'Aggressive Momentum Ignition',
            'price': 45250.00,
            'stop_loss': 44888.00,
            'take_profit': 45928.00,
            'timeframe': '5m',
            'timestamp': datetime.now()
        }
        
        formatted_signal = bot._format_trading_signal(test_signal)
        print("   ✅ Trading signal formatting successful")
        print(f"   📝 Sample signal length: {len(formatted_signal)} characters")
        
        # Test status update
        test_status = {
            'status': 'RUNNING',
            'uptime': '2:15:30',
            'total_signals': 5,
            'errors_count': 0,
            'active_jobs': 6,
            'current_time': datetime.now().strftime('%H:%M UTC')
        }
        
        formatted_status = bot._format_status_update(test_status)
        print("   ✅ Status update formatting successful")
        print(f"   📝 Sample status length: {len(formatted_status)} characters")
        
        # Test 5: Test message sending (optional)
        print("5. Testing message sending...")
        test_message = "🧪 <b>Integration Test</b>\n\nThis is a test message from the trading bot integration test.\n\nTime: " + datetime.now().strftime('%H:%M:%S UTC')
        
        if bot.send_message(test_message):
            print("   ✅ Test message sent successfully")
        else:
            print("   ⚠️  Test message failed (this might be expected if credentials are not set)")
        
        print("\n🎉 All Telegram integration tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        return False

def test_main_bot_integration():
    """Test the main bot's Telegram integration."""
    print("\n🔧 Testing Main Bot Telegram Integration")
    print("=" * 50)
    
    try:
        # Test 1: Import main bot
        print("1. Testing main bot import...")
        from enhanced_main import EnhancedTradingAlertBot
        print("   ✅ Main bot imported successfully")
        
        # Test 2: Check configuration
        print("2. Testing configuration...")
        from config import TELEGRAM_ALERTS_ENABLED, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        
        print(f"   📋 Telegram enabled: {TELEGRAM_ALERTS_ENABLED}")
        print(f"   🔑 Bot token set: {'Yes' if TELEGRAM_BOT_TOKEN else 'No'}")
        print(f"   💬 Chat ID set: {'Yes' if TELEGRAM_CHAT_ID else 'No'}")
        
        if TELEGRAM_ALERTS_ENABLED:
            print("   ✅ Telegram alerts are properly configured")
        else:
            print("   ⚠️  Telegram alerts are disabled (check your .env file)")
        
        # Test 3: Test bot initialization (without starting)
        print("3. Testing bot component initialization...")
        try:
            bot = EnhancedTradingAlertBot()
            print("   ✅ Bot components initialized successfully")
            
            # Check if Telegram bot was initialized
            if hasattr(bot, 'telegram_bot') and bot.telegram_bot:
                print("   ✅ Telegram bot component initialized")
            else:
                print("   ⚠️  Telegram bot component not initialized")
            
            # Cleanup
            bot.stop()
            print("   ✅ Bot cleanup completed")
            
        except Exception as e:
            print(f"   ❌ Bot initialization failed: {e}")
            return False
        
        print("\n🎉 Main bot Telegram integration tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Trading Bot Telegram Integration Test Suite")
    print("=" * 60)
    
    # Check environment
    print("🔍 Environment Check:")
    print(f"   📁 Working directory: {os.getcwd()}")
    print(f"   🐍 Python version: {sys.version}")
    print(f"   🔑 TELEGRAM_BOT_TOKEN: {'Set' if os.getenv('TELEGRAM_BOT_TOKEN') else 'Not set'}")
    print(f"   💬 TELEGRAM_CHAT_ID: {'Set' if os.getenv('TELEGRAM_CHAT_ID') else 'Not set'}")
    print()
    
    # Run tests
    telegram_test_passed = test_telegram_bot()
    main_bot_test_passed = test_main_bot_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"   🧪 Telegram Bot Tests: {'✅ PASSED' if telegram_test_passed else '❌ FAILED'}")
    print(f"   🔧 Main Bot Integration: {'✅ PASSED' if main_bot_test_passed else '❌ FAILED'}")
    
    if telegram_test_passed and main_bot_test_passed:
        print("\n🎉 ALL TESTS PASSED! Your Telegram integration is working correctly.")
        print("\n🚀 You can now deploy your bot to any hosting platform.")
        print("   Check DEPLOYMENT.md for detailed deployment instructions.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("   Make sure your .env file is properly configured.")
    
    return telegram_test_passed and main_bot_test_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
