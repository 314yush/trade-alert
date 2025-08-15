"""
Telegram Bot Module for the Risk-Adaptive Crypto Trading Alert Bot.

This module handles all Telegram bot operations including sending trading alerts,
status updates, and error notifications to the user.
"""

import logging
import time
import asyncio
import threading
from typing import Dict, List, Optional, Any
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError, NetworkError, InvalidToken
from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, DRY_RUN_MODE,
    MAX_RETRIES, RETRY_DELAY, DEBUG_MODE
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Handles Telegram bot operations for sending trading alerts.
    
    This class manages the Telegram bot connection, sends trading signals,
    and handles various types of notifications to the user.
    """
    
    def __init__(self):
        """Initialize the TelegramBot with bot token and chat ID."""
        self.bot = None
        self.chat_id = None
        self._loop = None
        self._loop_lock = threading.Lock()
        self._initialize_bot()
        
    def _initialize_bot(self) -> None:
        """
        Initialize the Telegram bot with the provided token.
        
        Validates the bot token and sets up the bot instance.
        """
        try:
            if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN_HERE':
                raise ValueError("Telegram bot token not configured. Please set TELEGRAM_BOT_TOKEN in config.py")
            
            if not TELEGRAM_CHAT_ID or TELEGRAM_CHAT_ID == 'YOUR_TELEGRAM_CHAT_ID_HERE':
                raise ValueError("Telegram chat ID not configured. Please set TELEGRAM_CHAT_ID in config.py")
            
            # Initialize bot
            self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
            self.chat_id = TELEGRAM_CHAT_ID
            
            # Test bot connection
            bot_info = asyncio.run(self.bot.get_me())
            logger.info(f"Telegram bot initialized successfully: @{bot_info.username}")
            
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise
        except InvalidToken as e:
            logger.error(f"Invalid bot token: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            raise
    
    def _get_or_create_loop(self):
        """
        Get the current event loop or create a new one for the current thread.
        This handles the case where we're called from a background thread.
        """
        try:
            # Try to get the current loop
            loop = asyncio.get_running_loop()
            return loop
        except RuntimeError:
            # No loop running in current thread, create one
            with self._loop_lock:
                if self._loop is None or not self._loop.is_running():
                    self._loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self._loop)
                return self._loop
    
    async def _send_message_async(self, message: str, parse_mode: str = ParseMode.HTML) -> bool:
        """
        Send a message to the configured Telegram chat (async version).
        
        Args:
            message (str): Message text to send
            parse_mode (str): Parse mode for the message (HTML, Markdown, etc.)
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if DRY_RUN_MODE:
            logger.info(f"[DRY RUN] Would send message: {message[:100]}...")
            return True
        
        if not self.bot or not self.chat_id:
            logger.error("Telegram bot not properly initialized")
            return False
        
        for attempt in range(MAX_RETRIES):
            try:
                logger.debug(f"Sending Telegram message (attempt {attempt + 1})")
                
                # Send the message
                result = await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode=parse_mode
                )
                
                logger.info(f"Message sent successfully. Message ID: {result.message_id}")
                return True
                
            except NetworkError as e:
                logger.warning(f"Network error on attempt {attempt + 1}: {e}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Failed to send message after {MAX_RETRIES} attempts due to network issues")
                    return False
                    
            except TelegramError as e:
                logger.error(f"Telegram error: {e}")
                return False
                
            except Exception as e:
                logger.error(f"Unexpected error sending message: {e}")
                return False
        
        return False
    
    def send_message(self, message: str, parse_mode: str = ParseMode.HTML) -> bool:
        """
        Send a message to the configured Telegram chat (sync wrapper).
        
        Args:
            message (str): Message text to send
            parse_mode (str): Parse mode for the message (HTML, Markdown, etc.)
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            # Get or create event loop for current thread
            loop = self._get_or_create_loop()
            
            # If we're in the main thread with a running loop, use asyncio.create_task
            if threading.current_thread() is threading.main_thread() and loop.is_running():
                # Schedule the coroutine in the main loop
                future = asyncio.run_coroutine_threadsafe(
                    self._send_message_async(message, parse_mode), 
                    loop
                )
                return future.result(timeout=30)  # 30 second timeout
            else:
                # Run in current thread's loop
                return loop.run_until_complete(self._send_message_async(message, parse_mode))
                
        except Exception as e:
            logger.error(f"Error in send_message wrapper: {e}")
            return False
    
    def send_trading_alert(self, signal: Dict[str, Any]) -> bool:
        """
        Send a trading alert based on the signal data.
        
        Args:
            signal (Dict[str, Any]): Trading signal information
            
        Returns:
            bool: True if alert sent successfully, False otherwise
        """
        try:
            # Format the alert message
            message = self._format_trading_alert(signal)
            
            # Send the message
            success = self.send_message(message)
            
            if success:
                logger.info(f"Trading alert sent successfully for {signal['profile']} strategy")
            else:
                logger.error(f"Failed to send trading alert for {signal['profile']} strategy")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending trading alert: {e}")
            return False
    
    def _format_trading_alert(self, signal: Dict[str, Any]) -> str:
        """
        Format a trading signal into a readable alert message.
        
        Args:
            signal (Dict[str, Any]): Trading signal information
            
        Returns:
            str: Formatted alert message
        """
        try:
            # Extract signal information
            profile = signal.get('profile', 'Unknown')
            strategy = signal.get('strategy', 'Unknown')
            signal_type = signal.get('signal_type', 'Unknown')
            symbol = signal.get('symbol', 'Unknown')
            timeframe = signal.get('timeframe', 'Unknown')
            price = signal.get('price', 0)
            timestamp = signal.get('timestamp', 'Unknown')
            
            # Format timestamp
            if hasattr(timestamp, 'strftime'):
                formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')
            else:
                formatted_time = str(timestamp)
            
            # Create the alert message
            message = f"""
🚨 <b>TRADING ALERT</b> 🚨

<b>Profile:</b> {profile}
<b>Strategy:</b> {strategy}
<b>Signal:</b> {signal_type.upper()}
<b>Symbol:</b> {symbol}
<b>Timeframe:</b> {timeframe}
<b>Price:</b> ${price:.2f}
<b>Time:</b> {formatted_time}

<i>Generated by Risk-Adaptive Crypto Trading Alert Bot</i>
"""
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"Error formatting trading alert: {e}")
            # Return a simple fallback message
            return f"Trading Alert: {signal.get('profile', 'Unknown')} - {signal.get('signal_type', 'Unknown')} signal"
    
    def send_status_update(self, message: str) -> bool:
        """
        Send a status update message.
        
        Args:
            message (str): Status message to send
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            formatted_message = f"📊 <b>STATUS UPDATE</b>\n\n{message}"
            return self.send_message(formatted_message)
            
        except Exception as e:
            logger.error(f"Error sending status update: {e}")
            return False
    
    def send_error_notification(self, error_message: str, context: str = "") -> bool:
        """
        Send an error notification message.
        
        Args:
            error_message (str): Error message to send
            context (str): Additional context about the error
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            message = f"⚠️ <b>ERROR NOTIFICATION</b>\n\n"
            if context:
                message += f"<b>Context:</b> {context}\n\n"
            message += f"<b>Error:</b> {error_message}"
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
            return False
    
    def send_startup_notification(self) -> bool:
        """
        Send a startup notification when the bot starts.
        
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            message = f"""
🤖 <b>BOT STARTUP</b>

Risk-Adaptive Crypto Trading Alert Bot is now running!

<b>Features:</b>
• Aggressive Strategy (5m timeframe)
• Moderate Strategy (15m timeframe)
• Conservative Strategy (1d timeframe)

<i>Monitoring for trading opportunities...</i>
"""
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending startup notification: {e}")
            return False
    
    def send_shutdown_notification(self) -> bool:
        """
        Send a shutdown notification when the bot stops.
        
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            message = f"""
🛑 <b>BOT SHUTDOWN</b>

Risk-Adaptive Crypto Trading Alert Bot is shutting down.

<i>Thank you for using the bot!</i>
"""
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending shutdown notification: {e}")
            return False
    
    def send_daily_summary(self, summary_data: Dict[str, Any]) -> bool:
        """
        Send a daily summary of bot activity.
        
        Args:
            summary_data (Dict[str, Any]): Summary data to include
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            message = f"""
📈 <b>DAILY SUMMARY</b>

<b>Date:</b> {summary_data.get('date', 'Unknown')}
<b>Signals Generated:</b> {summary_data.get('total_signals', 0)}
<b>Active Strategies:</b> {summary_data.get('active_strategies', 0)}
<b>Status:</b> {summary_data.get('status', 'Unknown')}

<i>Daily trading bot performance report</i>
"""
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
            return False
    
    async def _test_connection_async(self) -> bool:
        """
        Test the Telegram bot connection by sending a test message (async version).
        
        Returns:
            bool: True if connection test successful, False otherwise
        """
        try:
            test_message = "🧪 <b>CONNECTION TEST</b>\n\nThis is a test message to verify the Telegram bot connection."
            success = await self._send_message_async(test_message)
            
            if success:
                logger.info("Telegram bot connection test successful")
            else:
                logger.error("Telegram bot connection test failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error during connection test: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test the Telegram bot connection by sending a test message.
        
        Returns:
            bool: True if connection test successful, False otherwise
        """
        try:
            # Get or create event loop for current thread
            loop = self._get_or_create_loop()
            
            # If we're in the main thread with a running loop, use asyncio.create_task
            if threading.current_thread() is threading.main_thread() and loop.is_running():
                # Schedule the coroutine in the main loop
                future = asyncio.run_coroutine_threadsafe(
                    self._test_connection_async(), 
                    loop
                )
                return future.result(timeout=30)  # 30 second timeout
            else:
                # Run in current thread's loop
                return loop.run_until_complete(self._test_connection_async())
                
        except Exception as e:
            logger.error(f"Error in test_connection wrapper: {e}")
            return False
    
    async def _cleanup_async(self) -> None:
        """Clean up resources and close bot connection (async version)."""
        try:
            if self.bot:
                # Send shutdown notification before cleanup
                await self._send_message_async("🛑 Bot is shutting down...")
                
                # Close the bot session
                await self.bot.close()
                logger.info("Telegram bot connection closed")
                
        except Exception as e:
            logger.error(f"Error during Telegram bot cleanup: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources and close bot connection."""
        try:
            # Get or create event loop for current thread
            loop = self._get_or_create_loop()
            
            # If we're in the main thread with a running loop, use asyncio.create_task
            if threading.current_thread() is threading.main_thread() and loop.is_running():
                # Schedule the coroutine in the main loop
                future = asyncio.run_coroutine_threadsafe(
                    self._cleanup_async(), 
                    loop
                )
                future.result(timeout=30)  # 30 second timeout
            else:
                # Run in current thread's loop
                loop.run_until_complete(self._cleanup_async())
                
        except Exception as e:
            logger.error(f"Error in cleanup wrapper: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Test the TelegramBot
    try:
        bot = TelegramBot()
        
        # Test connection
        if bot.test_connection():
            print("Telegram bot connection test successful!")
            
            # Test sending a sample trading alert
            sample_signal = {
                'profile': 'Aggressive',
                'strategy': 'Momentum Ignition',
                'signal_type': 'long',
                'symbol': 'BTC/USDT',
                'timeframe': '5m',
                'price': 45000.00,
                'timestamp': '2024-01-01 12:00:00'
            }
            
            success = bot.send_trading_alert(sample_signal)
            if success:
                print("Sample trading alert sent successfully!")
            else:
                print("Failed to send sample trading alert")
        
        else:
            print("Telegram bot connection test failed!")
    
    except Exception as e:
        print(f"Test failed: {e}")
    
    finally:
        if 'bot' in locals():
            bot.cleanup()
