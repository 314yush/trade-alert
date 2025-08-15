#!/usr/bin/env python3
"""
Simple polling test to see if the bot can receive messages.
"""

import time
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_bot_controller import TelegramBotController

def main():
    print("🔄 Starting Simple Polling Test")
    print("=" * 40)
    
    try:
        # Create controller
        controller = TelegramBotController()
        
        if not controller.is_initialized:
            print("❌ Controller not initialized")
            return
        
        print("✅ Controller ready!")
        print("📱 Send a message to your bot now!")
        print("💡 Try: /help or /ping")
        print("⏱️  Polling for 60 seconds...")
        print("🛑 Press Ctrl+C to stop")
        
        # Start polling
        controller.start_polling()
        
        # Keep running for 60 seconds
        for i in range(60):
            time.sleep(1)
            if i % 10 == 0:
                print(f"   ⏱️  Still polling... {60-i} seconds left")
        
        print("⏰ Time's up! Stopping...")
        controller.stop_polling()
        
    except KeyboardInterrupt:
        print("\n⏹️  Stopping polling...")
        if 'controller' in locals():
            controller.stop_polling()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
