#!/usr/bin/env python3
"""
Test if the bot can process received messages.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_bot_controller import TelegramBotController

def test_message_processing():
    """Test if the bot can process received messages."""
    print("🧪 Testing Message Processing")
    print("=" * 40)
    
    try:
        # Create controller
        controller = TelegramBotController()
        
        if not controller.is_initialized:
            print("❌ Controller not initialized")
            return
        
        print("✅ Controller initialized")
        
        # Simulate processing the messages we know were received
        print("\n📝 Testing message processing:")
        
        # Test 1: Process /start command
        print("1. Testing /start command...")
        controller._handle_start("", {"chat": {"id": 5082620102}})
        
        # Test 2: Process /help command  
        print("2. Testing /help command...")
        controller._handle_help("", {"chat": {"id": 5082620102}})
        
        # Test 3: Process /ping command
        print("3. Testing /ping command...")
        controller._handle_ping("", {"chat": {"id": 5082620102}})
        
        print("\n✅ All command processing tests completed!")
        print("💡 Check your Telegram to see if you received responses!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_message_processing()
