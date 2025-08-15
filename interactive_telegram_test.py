#!/usr/bin/env python3
"""
Interactive Telegram test to see the full message flow.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_bot_controller import TelegramBotController

def interactive_test():
    """Interactive test of Telegram functionality."""
    print("🎮 Interactive Telegram Test")
    print("=" * 40)
    
    try:
        # Create controller
        controller = TelegramBotController()
        
        if not controller.is_initialized:
            print("❌ Controller not initialized")
            return
        
        print("✅ Controller initialized")
        print(f"✅ Chat ID: {controller.chat_id}")
        
        # Test 1: Send a direct message
        print("\n📤 Test 1: Sending direct message...")
        test_msg = "🧪 <b>Interactive Test</b>\n\nThis is a direct message test.\n\nTime: " + time.strftime('%H:%M:%S')
        if controller.send_message(test_msg):
            print("   ✅ Direct message sent!")
        else:
            print("   ❌ Failed to send direct message")
        
        # Test 2: Test command handlers
        print("\n📝 Test 2: Testing command handlers...")
        
        # Simulate a message from your chat
        fake_message = {
            "chat": {"id": int(controller.chat_id)},
            "text": "/help",
            "from": {"id": 12345, "first_name": "Test User"}
        }
        
        print("   📱 Simulating /help command...")
        controller._handle_message(fake_message)
        
        # Test 3: Test ping
        print("\n📝 Test 3: Testing ping command...")
        fake_message["text"] = "/ping"
        controller._handle_message(fake_message)
        
        # Test 4: Test info
        print("\n📝 Test 4: Testing info command...")
        fake_message["text"] = "/info"
        controller._handle_message(fake_message)
        
        print("\n✅ All tests completed!")
        print("💡 Check your Telegram for responses!")
        
        # Wait a moment for messages to be sent
        print("\n⏳ Waiting 3 seconds for messages to be sent...")
        time.sleep(3)
        
        print("\n🔍 Summary:")
        print("   • Direct message: Should have been sent")
        print("   • /help response: Should have been sent") 
        print("   • /ping response: Should have been sent")
        print("   • /info response: Should have been sent")
        
        print("\n❓ Did you receive any of these messages in Telegram?")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    interactive_test()
