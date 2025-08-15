#!/usr/bin/env python3
"""
Telegram Controlled Trading Bot Service

This service combines the Telegram bot controller with the trading bot,
allowing you to start, stop, and control the bot remotely via Telegram.
"""

import os
import sys
import time
import logging
import threading
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_bot_controller import TelegramBotController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TelegramControlledTradingBot:
    """
    Trading bot that can be controlled remotely via Telegram.
    """
    
    def __init__(self):
        """Initialize the controlled trading bot."""
        self.is_running = False
        self.start_time = None
        self.telegram_controller = None
        self.control_thread = None
        
        # Bot statistics
        self.stats = {
            'total_signals': 0,
            'errors_count': 0,
            'last_signal_time': None,
            'uptime': '00:00:00'
        }
        
        # Initialize Telegram controller
        self._initialize_telegram_controller()
        
        logger.info("Telegram Controlled Trading Bot initialized")
    
    def _initialize_telegram_controller(self) -> None:
        """Initialize the Telegram bot controller."""
        try:
            # Create controller with callback to this bot
            self.telegram_controller = TelegramBotController(
                bot_control_callback=self._handle_bot_control
            )
            
            if self.telegram_controller.is_initialized:
                logger.info("Telegram controller initialized successfully")
            else:
                logger.error("Failed to initialize Telegram controller")
                
        except Exception as e:
            logger.error(f"Error initializing Telegram controller: {e}")
            self.telegram_controller = None
    
    def _handle_bot_control(self, command: str, args: str) -> bool:
        """
        Handle bot control commands from Telegram.
        
        Args:
            command: The command to execute
            args: Additional arguments
            
        Returns:
            bool: True if command executed successfully
        """
        try:
            if command == 'start':
                return self._start_bot()
            elif command == 'stop':
                return self._stop_bot()
            elif command == 'status':
                return self._get_status()
            else:
                logger.warning(f"Unknown bot control command: {command}")
                return False
                
        except Exception as e:
            logger.error(f"Error handling bot control command {command}: {e}")
            return False
    
    def _start_bot(self) -> bool:
        """Start the trading bot."""
        if self.is_running:
            logger.info("Bot is already running")
            return False
        
        try:
            self.is_running = True
            self.start_time = datetime.now()
            
            # Start bot operations in background thread
            self.control_thread = threading.Thread(target=self._run_bot_operations, daemon=True)
            self.control_thread.start()
            
            logger.info("Trading bot started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            self.is_running = False
            return False
    
    def _stop_bot(self) -> bool:
        """Stop the trading bot."""
        if not self.is_running:
            logger.info("Bot is not currently running")
            return False
        
        try:
            self.is_running = False
            
            # Wait for control thread to finish
            if self.control_thread and self.control_thread.is_alive():
                self.control_thread.join(timeout=5)
            
            logger.info("Trading bot stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            return False
    
    def _get_status(self) -> str:
        """Get current bot status."""
        try:
            if self.start_time:
                uptime = datetime.now() - self.start_time
                hours, remainder = divmod(int(uptime.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                uptime_str = "00:00:00"
            
            status_text = f"""
📊 <b>TRADING BOT STATUS</b>

<b>Status:</b> {'🟢 RUNNING' if self.is_running else '🔴 STOPPED'}
<b>Uptime:</b> {uptime_str}
<b>Total Signals:</b> {self.stats['total_signals']}
<b>Errors:</b> {self.stats['errors_count']}
<b>Last Signal:</b> {self.stats['last_signal_time'] or 'None'}

<b>Time:</b> {datetime.now().strftime('%H:%M:%S UTC')}
            """
            
            return status_text.strip()
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return "❌ Error retrieving status"
    
    def _run_bot_operations(self) -> None:
        """Run the main bot operations in background thread."""
        logger.info("Bot operations thread started")
        
        while self.is_running:
            try:
                # Simulate trading bot operations
                # In a real implementation, this would run your actual trading strategies
                
                # Update uptime
                if self.start_time:
                    uptime = datetime.now() - self.start_time
                    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    self.stats['uptime'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                # Simulate some work
                time.sleep(5)
                
                # Send periodic status updates (every 5 minutes)
                if self.start_time and (datetime.now() - self.start_time).seconds % 300 < 5:
                    if self.telegram_controller:
                        self.telegram_controller.send_message(
                            f"📊 <b>Bot Status Update</b>\n\n"
                            f"Status: {'🟢 RUNNING' if self.is_running else '🔴 STOPPED'}\n"
                            f"Uptime: {self.stats['uptime']}\n"
                            f"Signals: {self.stats['total_signals']}\n"
                            f"Errors: {self.stats['errors_count']}"
                        )
                
            except Exception as e:
                logger.error(f"Error in bot operations: {e}")
                self.stats['errors_count'] += 1
                time.sleep(10)  # Wait longer on error
        
        logger.info("Bot operations thread stopped")
    
    def start(self) -> None:
        """Start the Telegram controlled trading bot service."""
        try:
            logger.info("Starting Telegram Controlled Trading Bot Service...")
            
            # Start Telegram controller polling
            if self.telegram_controller:
                self.telegram_controller.start_polling()
                logger.info("Telegram controller polling started")
            
            # Keep main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
            
        except Exception as e:
            logger.error(f"Error starting service: {e}")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the service."""
        try:
            logger.info("Stopping Telegram Controlled Trading Bot Service...")
            
            # Stop bot operations
            self._stop_bot()
            
            # Stop Telegram controller
            if self.telegram_controller:
                self.telegram_controller.cleanup()
                logger.info("Telegram controller stopped")
            
            logger.info("Service stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping service: {e}")


def main():
    """Main function to run the Telegram controlled trading bot."""
    try:
        # Create and start the service
        bot = TelegramControlledTradingBot()
        bot.start()
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
