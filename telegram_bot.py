"""
Telegram Bot Module for Enhanced Trading Alert Bot

This module handles all Telegram bot operations with a simple, synchronous approach
to avoid async event loop conflicts.
"""

import logging
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Simple Telegram bot for sending trading alerts and status updates.
    
    This class uses the Telegram HTTP API directly to avoid async complexity.
    """
    
    def __init__(self):
        """Initialize the Telegram bot."""
        self.bot_token = None
        self.chat_id = None
        self.is_initialized = False
        
        try:
            self._initialize_bot()
            logger.info("Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
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
            
            # Mark as initialized first
            self.is_initialized = True
            logger.info(f"Telegram bot initialized for chat ID: {chat_id}")
            
            # Test connection after initialization
            if self._test_connection():
                logger.info("Telegram connection test successful")
            else:
                logger.warning("Telegram connection test failed, but bot will continue")
            
        except Exception as e:
            logger.error(f"Error initializing Telegram bot: {e}")
            self.is_initialized = False
            raise
    
    def _test_connection(self) -> bool:
        """Test the bot connection using HTTP API."""
        try:
            # Send a test message
            test_message = "🧪 <b>Telegram Bot Test</b>\n\nBot is working correctly! ✅"
            success = self.send_message(test_message)
            
            if success:
                logger.info("Telegram bot connection test successful")
            else:
                logger.warning("Telegram bot connection test failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error testing Telegram connection: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test the Telegram bot connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not self.is_initialized:
            logger.warning("Telegram bot not initialized")
            return False
        
        try:
            # Send a test message
            test_message = "🧪 <b>Telegram Bot Test</b>\n\nBot is working correctly! ✅"
            success = self.send_message(test_message)
            
            if success:
                logger.info("Telegram bot connection test successful")
            else:
                logger.warning("Telegram bot connection test failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error testing Telegram connection: {e}")
            return False
    
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
    
    def send_trading_signal(self, signal: Dict[str, Any]) -> bool:
        """
        Send a formatted trading signal to Telegram.
        
        Args:
            signal (Dict[str, Any]): Trading signal data
            
        Returns:
            bool: True if signal sent successfully, False otherwise
        """
        try:
            # Format the trading signal
            message = self._format_trading_signal(signal)
            
            # Send to Telegram
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending trading signal to Telegram: {e}")
            return False
    
    def send_status_update(self, status: Dict[str, Any]) -> bool:
        """
        Send a status update to Telegram.
        
        Args:
            status (Dict[str, Any]): Bot status data
            
        Returns:
            bool: True if status sent successfully, False otherwise
        """
        try:
            # Format the status update
            message = self._format_status_update(status)
            
            # Send to Telegram
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending status update to Telegram: {e}")
            return False
    
    def send_daily_summary(self, summary: Dict[str, Any]) -> bool:
        """
        Send a daily summary to Telegram.
        
        Args:
            summary (Dict[str, Any]): Daily summary data
            
        Returns:
            bool: True if summary sent successfully, False otherwise
        """
        try:
            # Format the daily summary
            message = self._format_daily_summary(summary)
            
            # Send to Telegram
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending daily summary to Telegram: {e}")
            return False
    
    def _format_trading_signal(self, signal: Dict[str, Any]) -> str:
        """Format a trading signal for Telegram."""
        try:
            # Get strategy emoji and risk level
            strategy_info = {
                'Aggressive Momentum Ignition': ('🚨', 'HIGH RISK'),
                'Moderate EMA Crossover': ('⚖️', 'MEDIUM RISK'),
                'Conservative Trend Rider': ('🛡️', 'LOW RISK')
            }.get(signal.get('profile', ''), ('📊', 'UNKNOWN'))
            
            strategy_emoji, risk_level = strategy_info
            
            # Get signal emoji
            signal_emoji = '🟢' if signal.get('signal_type') == 'long' else '🔴'
            
            # Format message
            message = f"{strategy_emoji} <b>TRADING SIGNAL</b> {signal_emoji}\n\n"
            message += f"<b>Action:</b> {signal.get('signal_type', 'UNKNOWN').upper()}\n"
            message += f"<b>Asset:</b> {signal.get('symbol', 'UNKNOWN')}\n"
            message += f"<b>Strategy:</b> {signal.get('profile', 'UNKNOWN')}\n"
            message += f"<b>Risk Level:</b> {risk_level}\n"
            message += f"<b>Timeframe:</b> {signal.get('timeframe', 'UNKNOWN')}\n\n"
            
            message += f"<b>Entry:</b> ${signal.get('price', 0):,.2f}\n"
            message += f"<b>Stop Loss:</b> ${signal.get('stop_loss', 0):,.2f}\n"
            message += f"<b>Take Profit:</b> ${signal.get('take_profit', 0):,.2f}\n\n"
            
            # Add additional parameters if available
            if 'leverage' in signal:
                message += f"<b>Leverage:</b> {signal['leverage']}x\n"
            
            if 'position_size' in signal:
                message += f"<b>Position Size:</b> {signal['position_size']}\n"
            
            # Add timestamp
            timestamp = signal.get('timestamp')
            if timestamp:
                message += f"\n<b>Time:</b> {timestamp.strftime('%H:%M UTC')}\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting trading signal: {e}")
            return f"🚨 Trading Signal: {signal.get('signal_type', 'UNKNOWN')} {signal.get('symbol', 'UNKNOWN')}"
    
    def _format_status_update(self, status: Dict[str, Any]) -> str:
        """Format a status update for Telegram."""
        try:
            message = f"📊 <b>BOT STATUS UPDATE</b>\n\n"
            message += f"<b>Status:</b> 🟢 {status.get('status', 'UNKNOWN')}\n"
            message += f"<b>Uptime:</b> {status.get('uptime', 'UNKNOWN')}\n"
            message += f"<b>Total Signals:</b> {status.get('total_signals', 0)}\n"
            message += f"<b>Errors:</b> {status.get('errors_count', 0)}\n"
            message += f"<b>Active Jobs:</b> {status.get('active_jobs', 0)}\n"
            message += f"<b>Time:</b> {status.get('current_time', 'UNKNOWN')}\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting status update: {e}")
            return "📊 Bot Status Update"
    
    def _format_daily_summary(self, summary: Dict[str, Any]) -> str:
        """Format a daily summary for Telegram."""
        try:
            message = f"📈 <b>DAILY TRADING SUMMARY</b>\n\n"
            message += f"<b>Date:</b> {summary.get('date', 'UNKNOWN')}\n"
            message += f"<b>Total Signals:</b> {summary.get('total_signals', 0)}\n\n"
            
            message += "<b>Signals by Strategy:</b>\n"
            for strategy, count in summary.get('signals_by_strategy', {}).items():
                strategy_name = strategy.replace('_', ' ').title()
                message += f"  {strategy_name}: {count}\n"
            
            message += f"\n<b>Errors:</b> {summary.get('errors_count', 0)}\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting daily summary: {e}")
            return "📈 Daily Trading Summary"
    
    def cleanup(self) -> None:
        """Clean up Telegram bot resources."""
        try:
            # Nothing to clean up with HTTP API approach
            logger.info("Telegram bot cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during Telegram bot cleanup: {e}")


# Test the bot if run directly
if __name__ == "__main__":
    # Test Telegram bot
    try:
        bot = TelegramBot()
        if bot.is_initialized:
            print("✅ Telegram bot initialized successfully")
            
            # Test connection
            if bot.test_connection():
                print("✅ Telegram connection test successful")
            else:
                print("❌ Telegram connection test failed")
        else:
            print("❌ Telegram bot initialization failed")
            
    except Exception as e:
        print(f"❌ Error testing Telegram bot: {e}")
    finally:
        # Cleanup
        if 'bot' in locals():
            bot.cleanup()
