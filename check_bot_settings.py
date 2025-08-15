#!/usr/bin/env python3
"""
Check bot settings and permissions.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_bot_settings():
    """Check various bot settings."""
    print("🔍 Checking Bot Settings and Permissions")
    print("=" * 50)
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return
    
    print(f"✅ Bot Token: {bot_token[:10]}...")
    
    # Check bot info
    print("\n🤖 Bot Information:")
    print("-" * 30)
    
    bot_url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        response = requests.get(bot_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                bot_info = data['result']
                print(f"✅ Name: {bot_info.get('first_name')}")
                print(f"✅ Username: @{bot_info.get('username')}")
                print(f"✅ ID: {bot_info.get('id')}")
                print(f"✅ Can Join Groups: {bot_info.get('can_join_groups', 'Unknown')}")
                print(f"✅ Can Read All Group Messages: {bot_info.get('can_read_all_group_messages', 'Unknown')}")
                print(f"✅ Supports Inline Queries: {bot_info.get('supports_inline_queries', 'Unknown')}")
            else:
                print("❌ Could not get bot info")
        else:
            print(f"❌ Bot info request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting bot info: {e}")
    
    # Check webhook info
    print("\n🌐 Webhook Information:")
    print("-" * 30)
    
    webhook_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    try:
        response = requests.get(webhook_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                webhook_info = data['result']
                print(f"✅ URL: {webhook_info.get('url', 'Not set')}")
                print(f"✅ Has Custom Certificate: {webhook_info.get('has_custom_certificate', 'Unknown')}")
                print(f"✅ Pending Update Count: {webhook_info.get('pending_update_count', 'Unknown')}")
                print(f"✅ Last Error Date: {webhook_info.get('last_error_date', 'None')}")
                print(f"✅ Last Error Message: {webhook_info.get('last_error_message', 'None')}")
                
                if webhook_info.get('url'):
                    print("⚠️  Webhook is set - this might interfere with polling!")
                else:
                    print("✅ No webhook set - polling should work")
            else:
                print("❌ Could not get webhook info")
        else:
            print(f"❌ Webhook info request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting webhook info: {e}")
    
    # Check updates
    print("\n📡 Update Information:")
    print("-" * 30)
    
    updates_url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        response = requests.get(updates_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                updates = data['result']
                print(f"✅ Updates found: {len(updates)}")
                
                if updates:
                    print("📝 Recent messages:")
                    for i, update in enumerate(updates[-3:]):
                        if 'message' in update:
                            msg = update['message']
                            chat = msg.get('chat', {})
                            text = msg.get('text', 'No text')
                            print(f"   {i+1}. Chat ID: {chat.get('id')} | Text: {text}")
                else:
                    print("📭 No updates found")
                    print("💡 This means the bot hasn't received any messages yet")
            else:
                print(f"❌ Could not get updates: {data}")
        else:
            print(f"❌ Updates request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting updates: {e}")
    
    print("\n🔧 Troubleshooting Steps:")
    print("=" * 50)
    print("1. Go to @BotFather and check Group Privacy settings")
    print("2. Make sure to send /start to your bot first")
    print("3. Check if webhook is interfering with polling")
    print("4. Verify bot permissions in Telegram")

if __name__ == "__main__":
    check_bot_settings()
