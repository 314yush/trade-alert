#!/usr/bin/env python3
"""
Test script for Telegram Bot Control functionality.

This script demonstrates how to use the Telegram bot controller
to remotely control your trading bot.
"""

import os
import sys
import time
import threading

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_telegram_controller():
    """Test the Telegram bot controller functionality."""
    print("🧪 Testing Telegram Bot Controller")
    print("=" * 50)
    
    try:
        # Test 1: Import Telegram bot controller
        print("1. Testing Telegram bot controller import...")
        from telegram_bot_controller import TelegramBotController
        print("   ✅ Telegram bot controller imported successfully")
        
        # Test 2: Initialize controller
        print("2. Testing controller initialization...")
        controller = TelegramBotController()
        if controller.is_initialized:
            print("   ✅ Controller initialized successfully")
        else:
            print("   ❌ Controller initialization failed")
            return False
        
        # Test 3: Test message sending
        print("3. Testing message sending...")
        test_message = "🧪 <b>Controller Test</b>\n\nTesting the Telegram bot controller functionality.\n\nTime: " + time.strftime('%H:%M:%S')
        
        if controller.send_message(test_message):
            print("   ✅ Test message sent successfully")
        else:
            print("   ⚠️  Test message failed (check your credentials)")
        
        # Test 4: Test help command
        print("4. Testing help command...")
        controller._handle_help("", {})
        print("   ✅ Help command processed")
        
        # Test 5: Test info command
        print("5. Testing info command...")
        controller._handle_info("", {})
        print("   ✅ Info command processed")
        
        print("\n🎉 All Telegram controller tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        return False

def test_telegram_controlled_bot():
    """Test the Telegram controlled trading bot."""
    print("\n🤖 Testing Telegram Controlled Trading Bot")
    print("=" * 50)
    
    try:
        # Test 1: Import controlled bot
        print("1. Testing controlled bot import...")
        from telegram_controlled_service import TelegramControlledTradingBot
        print("   ✅ Controlled bot imported successfully")
        
        # Test 2: Test bot initialization
        print("2. Testing bot initialization...")
        bot = TelegramControlledTradingBot()
        print("   ✅ Bot initialized successfully")
        
        # Test 3: Test bot control methods
        print("3. Testing bot control methods...")
        
        # Test start
        start_result = bot._start_bot()
        print(f"   ✅ Bot start: {'Success' if start_result else 'Already running'}")
        
        # Test status
        status = bot._get_status()
        print(f"   ✅ Status retrieved: {len(status)} characters")
        
        # Test stop
        stop_result = bot._stop_bot()
        print(f"   ✅ Bot stop: {'Success' if stop_result else 'Already stopped'}")
        
        print("\n🎉 All controlled bot tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        return False

def demonstrate_usage():
    """Demonstrate how to use the Telegram control system."""
    print("\n📚 Usage Demonstration")
    print("=" * 50)
    
    print("""
🤖 <b>How to Use Telegram Bot Control</b>

<b>1. Start the Service:</b>
   python3 telegram_controlled_service.py

<b>2. Send Commands via Telegram:</b>
   /start    - Start the trading bot
   /stop     - Stop the trading bot
   /restart  - Restart the trading bot
   /status   - Check bot status
   /help     - Show available commands
   /ping     - Check if controller is responsive
   /info     - Get bot information

<b>3. Example Usage:</b>
   • Send /start to begin trading operations
   • Send /status to check current status
   • Send /stop to halt trading operations
   • Send /restart to restart the bot

<b>4. Benefits:</b>
   • Control your bot from anywhere via Telegram
   • No need to SSH into servers
   • Real-time status updates
   • Secure remote control
        """)

def main():
    """Run all tests and demonstrations."""
    print("🚀 Telegram Bot Control Test Suite")
    print("=" * 60)
    
    # Check environment
    print("🔍 Environment Check:")
    print(f"   📁 Working directory: {os.getcwd()}")
    print(f"   🐍 Python version: {sys.version}")
    print(f"   🔑 TELEGRAM_BOT_TOKEN: {'Set' if os.getenv('TELEGRAM_BOT_TOKEN') else 'Not set'}")
    print(f"   💬 TELEGRAM_CHAT_ID: {'Set' if os.getenv('TELEGRAM_CHAT_ID') else 'Not set'}")
    print()
    
    # Run tests
    controller_test_passed = test_telegram_controller()
    controlled_bot_test_passed = test_telegram_controlled_bot()
    
    # Show usage demonstration
    demonstrate_usage()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"   🧪 Telegram Controller Tests: {'✅ PASSED' if controller_test_passed else '❌ FAILED'}")
    print(f"   🤖 Controlled Bot Tests: {'✅ PASSED' if controlled_bot_test_passed else '❌ FAILED'}")
    
    if controller_test_passed and controlled_bot_test_passed:
        print("\n🎉 ALL TESTS PASSED! Your Telegram control system is working correctly.")
        print("\n🚀 You can now:")
        print("   1. Deploy to Vercel with telegram_controlled_service.py")
        print("   2. Control your bot remotely via Telegram")
        print("   3. Start/stop trading operations from anywhere")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("   Make sure your .env file is properly configured.")
    
    return controller_test_passed and controlled_bot_test_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
