#!/usr/bin/env python3
"""
Real polling test that will actually listen for Telegram messages.
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

def real_polling_test():
    """Real polling test."""
    print("🔄 Real Polling Test - Listening for Messages")
    print("=" * 50)
    
    try:
        # Create controller
        controller = TelegramBotController()
        
        if not controller.is_initialized:
            print("❌ Controller not initialized")
            return
        
        print("✅ Controller initialized")
        print(f"✅ Chat ID: {controller.chat_id}")
        
        # Send startup message
        print("\n📤 Sending startup message...")
        controller.send_message("🔄 <b>Polling Test Started</b>\n\nI'm now listening for your messages!\n\nSend me a command like /help or /ping")
        
        # Start polling
        print("\n🔄 Starting polling...")
        controller.start_polling()
        
        print("✅ Polling started!")
        print("📱 Now send a message to your bot on Telegram!")
        print("💡 Try: /help, /ping, /info, or just type 'hello'")
        print("⏱️  I'll listen for 60 seconds...")
        print("🛑 Press Ctrl+C to stop early")
        
        # Listen for 60 seconds
        for i in range(60):
            time.sleep(1)
            if i % 10 == 0:
                print(f"   ⏱️  Listening... {60-i} seconds left")
        
        print("\n⏰ Time's up! Stopping...")
        controller.stop_polling()
        
    except KeyboardInterrupt:
        print("\n⏹️  Stopping polling...")
        if 'controller' in locals():
            controller.stop_polling()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    real_polling_test()
