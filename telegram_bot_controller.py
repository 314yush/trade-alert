#!/usr/bin/env python3
"""
Enhanced Telegram Bot Controller for Trading Alert Bot

This module provides a Telegram bot that can control the trading bot remotely,
including starting, stopping, and checking status via Telegram commands.
"""

import logging
import os
import time
import threading
from typing import Dict, Any, Optional, Callable
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class TelegramBotController:
    """
    Enhanced Telegram bot controller with command handling capabilities.
    
    This class can receive commands from Telegram and control the trading bot.
    """
    
    def __init__(self, bot_control_callback: Optional[Callable] = None):
        """
        Initialize the Telegram bot controller.
        
        Args:
            bot_control_callback: Function to call for bot control commands
        """
        self.bot_token = None
        self.chat_id = None
        self.is_initialized = False
        self.is_running = False
        self.update_thread = None
        self.bot_control_callback = bot_control_callback
        
        # Command handlers
        self.command_handlers = {
            '/start': self._handle_start,
            '/stop': self._handle_stop,
            '/status': self._handle_status,
            '/help': self._handle_help,
            '/restart': self._handle_restart,
            '/ping': self._handle_ping,
            '/info': self._handle_info
        }
        
        try:
            self._initialize_bot()
            logger.info("Telegram bot controller initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot controller: {e}")
            self.is_initialized = False
    
    def _initialize_bot(self) -> None:
        """Initialize the bot with token and chat ID from environment."""
        try:
            # Get bot token from environment
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            if not bot_token:
                raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")
            
            # Get chat ID from environment
            chat_id = os.getenv('TELEGRAM_CHAT_ID')
            if not chat_id:
                raise ValueError("TELEGRAM_CHAT_ID not found in environment")
            
            # Store credentials
            self.bot_token = bot_token
            self.chat_id = chat_id
            
            # Mark as initialized
            self.is_initialized = True
            logger.info(f"Telegram bot controller initialized for chat ID: {chat_id}")
            
        except Exception as e:
            logger.error(f"Error initializing Telegram bot controller: {e}")
            self.is_initialized = False
            raise
    
    def start_polling(self) -> None:
        """Start polling for Telegram updates."""
        if not self.is_initialized:
            logger.error("Bot not initialized, cannot start polling")
            return
        
        self.is_running = True
        self.update_thread = threading.Thread(target=self._poll_updates, daemon=True)
        self.update_thread.start()
        logger.info("Started polling for Telegram updates")
        
        # Send startup message
        self.send_message("🤖 <b>Trading Bot Controller Started</b>\n\n"
                         "I'm now listening for your commands!\n"
                         "Use /help to see available commands.")
    
    def stop_polling(self) -> None:
        """Stop polling for Telegram updates."""
        self.is_running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=5)
        logger.info("Stopped polling for Telegram updates")
    
    def _poll_updates(self) -> None:
        """Poll for Telegram updates in a separate thread."""
        offset = 0
        
        while self.is_running:
            try:
                # Get updates from Telegram
                url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
                params = {
                    'offset': offset,
                    'timeout': 30,
                    'allowed_updates': ['message']
                }
                
                response = requests.get(url, params=params, timeout=35)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data['ok'] and data['result']:
                        for update in data['result']:
                            if 'message' in update:
                                self._handle_message(update['message'])
                            offset = update['update_id'] + 1
                
                time.sleep(1)  # Small delay between polls
                
            except Exception as e:
                logger.error(f"Error polling Telegram updates: {e}")
                time.sleep(5)  # Wait longer on error
    
    def _handle_message(self, message: Dict[str, Any]) -> None:
        """Handle incoming Telegram messages."""
        try:
            # Check if message is from authorized chat
            if str(message.get('chat', {}).get('id')) != str(self.chat_id):
                logger.warning(f"Unauthorized message from chat ID: {message.get('chat', {}).get('id')}")
                return
            
            # Extract text and handle commands
            text = message.get('text', '').strip()
            if text.startswith('/'):
                self._handle_command(text, message)
            else:
                # Handle regular messages
                self._handle_regular_message(text, message)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    def _handle_command(self, command: str, message: Dict[str, Any]) -> None:
        """Handle Telegram bot commands."""
        try:
            # Split command and arguments
            parts = command.split(' ', 1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            # Find and execute command handler
            if cmd in self.command_handlers:
                self.command_handlers[cmd](args, message)
            else:
                self.send_message(f"❓ Unknown command: {cmd}\nUse /help to see available commands.")
                
        except Exception as e:
            logger.error(f"Error handling command {command}: {e}")
            self.send_message("❌ Error processing command. Please try again.")
    
    def _handle_start(self, args: str, message: Dict[str, Any]) -> None:
        """Handle /start command."""
        if self.bot_control_callback:
            try:
                result = self.bot_control_callback('start', args)
                if result:
                    self.send_message("🚀 <b>Trading Bot Started</b>\n\n"
                                    "Your trading bot is now running and monitoring the markets!")
                else:
                    self.send_message("⚠️ <b>Bot Already Running</b>\n\n"
                                    "The trading bot is already active.")
            except Exception as e:
                self.send_message(f"❌ <b>Error Starting Bot</b>\n\n{str(e)}")
        else:
            self.send_message("🚀 <b>Welcome to Trading Bot Controller!</b>\n\n"
                            "Use /help to see available commands.\n"
                            "Note: Bot control callback not configured.")
    
    def _handle_stop(self, args: str, message: Dict[str, Any]) -> None:
        """Handle /stop command."""
        if self.bot_control_callback:
            try:
                result = self.bot_control_callback('stop', args)
                if result:
                    self.send_message("🛑 <b>Trading Bot Stopped</b>\n\n"
                                    "Your trading bot has been stopped.")
                else:
                    self.send_message("⚠️ <b>Bot Already Stopped</b>\n\n"
                                    "The trading bot is not currently running.")
            except Exception as e:
                self.send_message(f"❌ <b>Error Stopping Bot</b>\n\n{str(e)}")
        else:
            self.send_message("🛑 <b>Stop Command Received</b>\n\n"
                            "Note: Bot control callback not configured.")
    
    def _handle_status(self, args: str, message: Dict[str, Any]) -> None:
        """Handle /status command."""
        if self.bot_control_callback:
            try:
                status = self.bot_control_callback('status', args)
                if status:
                    self.send_message(f"📊 <b>Bot Status</b>\n\n{status}")
                else:
                    self.send_message("❓ <b>Status Unknown</b>\n\n"
                                    "Unable to retrieve bot status.")
            except Exception as e:
                self.send_message(f"❌ <b>Error Getting Status</b>\n\n{str(e)}")
        else:
            self.send_message("📊 <b>Status Command Received</b>\n\n"
                            "Note: Bot control callback not configured.")
    
    def _handle_help(self, args: str, message: Dict[str, Any]) -> None:
        """Handle /help command."""
        help_text = """
🤖 <b>Trading Bot Controller Commands</b>

<b>Bot Control:</b>
/start - Start the trading bot
/stop - Stop the trading bot
/restart - Restart the trading bot
/status - Check bot status

<b>Information:</b>
/help - Show this help message
/ping - Check if controller is responsive
/info - Get bot information

<b>Usage:</b>
Just send any of these commands in this chat to control your trading bot remotely!
        """
        self.send_message(help_text.strip())
    
    def _handle_restart(self, args: str, message: Dict[str, Any]) -> None:
        """Handle /restart command."""
        if self.bot_control_callback:
            try:
                # Stop first
                self.bot_control_callback('stop', args)
                time.sleep(2)  # Wait a bit
                # Start again
                result = self.bot_control_callback('start', args)
                if result:
                    self.send_message("🔄 <b>Trading Bot Restarted</b>\n\n"
                                    "Your trading bot has been restarted successfully!")
                else:
                    self.send_message("⚠️ <b>Restart Failed</b>\n\n"
                                    "Unable to restart the trading bot.")
            except Exception as e:
                self.send_message(f"❌ <b>Error Restarting Bot</b>\n\n{str(e)}")
        else:
            self.send_message("🔄 <b>Restart Command Received</b>\n\n"
                            "Note: Bot control callback not configured.")
    
    def _handle_ping(self, args: str, message: Dict[str, Any]) -> None:
        """Handle /ping command."""
        self.send_message("🏓 <b>Pong!</b>\n\n"
                         "Trading Bot Controller is responsive and running.")
    
    def _handle_info(self, args: str, message: Dict[str, Any]) -> None:
        """Handle /info command."""
        info_text = f"""
ℹ️ <b>Bot Information</b>

<b>Controller Status:</b>
• Running: {'Yes' if self.is_running else 'No'}
• Initialized: {'Yes' if self.is_initialized else 'No'}
• Chat ID: {self.chat_id}

<b>Available Commands:</b>
• /start, /stop, /restart
• /status, /help, /ping, /info

<b>Features:</b>
• Remote bot control via Telegram
• Real-time status monitoring
• Secure command execution
        """
        self.send_message(info_text.strip())
    
    def _handle_regular_message(self, text: str, message: Dict[str, Any]) -> None:
        """Handle regular (non-command) messages."""
        # You can customize this to handle regular messages
        # For now, just acknowledge them
        if text.lower() in ['hello', 'hi', 'hey']:
            self.send_message("👋 Hello! Use /help to see available commands.")
        elif text.lower() in ['thanks', 'thank you', 'thx']:
            self.send_message("You're welcome! 😊")
        else:
            self.send_message("💬 I received your message. Use /help to see what I can do!")
    
    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        Send a message to Telegram using HTTP API.
        
        Args:
            message (str): Message to send
            parse_mode (str): Parse mode (HTML, Markdown, etc.)
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.is_initialized:
            logger.warning("Telegram bot not initialized, cannot send message")
            return False
        
        try:
            # Use Telegram HTTP API directly
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                logger.info("Message sent to Telegram successfully")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error sending Telegram message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up Telegram bot controller resources."""
        try:
            self.stop_polling()
            logger.info("Telegram bot controller cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during Telegram bot controller cleanup: {e}")


# Test the controller if run directly
if __name__ == "__main__":
    # Test Telegram bot controller
    try:
        controller = TelegramBotController()
        if controller.is_initialized:
            print("✅ Telegram bot controller initialized successfully")
            
            # Test message sending
            if controller.send_message("🧪 <b>Controller Test</b>\n\nController is working correctly! ✅"):
                print("✅ Message sending test successful")
            else:
                print("❌ Message sending test failed")
                
        else:
            print("❌ Telegram bot controller initialization failed")
            
    except Exception as e:
        print(f"❌ Error testing Telegram bot controller: {e}")
    finally:
        # Cleanup
        if 'controller' in locals():
            controller.cleanup()
