#!/usr/bin/env python3
"""
Check if the bot can receive Telegram updates.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_telegram_updates():
    """Check Telegram updates manually."""
    print("🔍 Checking Telegram Updates Manually")
    print("=" * 40)
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID not set")
        return
    
    print(f"✅ Bot Token: {bot_token[:10]}...")
    print(f"✅ Chat ID: {chat_id}")
    
    # Get updates from Telegram
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        print("\n📡 Fetching updates from Telegram...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['ok']:
                updates = data['result']
                print(f"✅ Successfully connected to Telegram API")
                print(f"📊 Found {len(updates)} updates")
                
                if updates:
                    print("\n📝 Recent updates:")
                    for i, update in enumerate(updates[-3:]):  # Show last 3
                        if 'message' in update:
                            msg = update['message']
                            chat = msg.get('chat', {})
                            text = msg.get('text', 'No text')
                            print(f"   {i+1}. Chat ID: {chat.get('id')} | Text: {text}")
                else:
                    print("📭 No updates found")
                    print("💡 Try sending a message to your bot first!")
                
                # Check bot info
                print("\n🤖 Checking bot info...")
                bot_url = f"https://api.telegram.org/bot{bot_token}/getMe"
                bot_response = requests.get(bot_url, timeout=10)
                
                if bot_response.status_code == 200:
                    bot_data = bot_response.json()
                    if bot_data['ok']:
                        bot_info = bot_data['result']
                        print(f"✅ Bot Name: {bot_info.get('first_name')}")
                        print(f"✅ Bot Username: @{bot_info.get('username')}")
                        print(f"✅ Bot ID: {bot_info.get('id')}")
                        
                        print(f"\n💡 To test your bot:")
                        print(f"   1. Search for @{bot_info.get('username')} on Telegram")
                        print(f"   2. Click 'Start' or send /start")
                        print(f"   3. Send a message like /help")
                        print(f"   4. Run this script again to see updates")
                    else:
                        print("❌ Could not get bot info")
                else:
                    print(f"❌ Bot info request failed: {bot_response.status_code}")
                    
            else:
                print(f"❌ Telegram API error: {data}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_telegram_updates()
