#!/usr/bin/env python3
"""
Enhanced Main Application Module for the Risk-Adaptive Crypto Trading Alert Bot.

This module orchestrates the enhanced strategies with sophisticated risk management,
position sizing, and multi-timeframe analysis. It sends detailed trading alerts
via Telegram with comprehensive trade information.
"""

import logging
import signal
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from config import (
    ENABLED_PROFILES, SCHEDULE_INTERVALS, TRADING_PAIRS, DEFAULT_PAIR,
    LOG_LEVEL, LOG_FILE, DEBUG_MODE, DRY_RUN_MODE, CAPITAL_ALLOCATION,
    CONSOLE_ALERTS_ENABLED
)
from enhanced_strategy_engine import EnhancedStrategyEngine

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class EnhancedTradingAlertBot:
    """
    Enhanced trading alert bot with sophisticated strategies and risk management.
    
    This class manages the enhanced strategy engine, processes trading signals,
    and sends detailed alerts via Telegram. It implements professional-grade
    risk management and comprehensive performance tracking.
    """
    
    def __init__(self):
        """Initialize the EnhancedTradingAlertBot with all necessary components."""
        self.scheduler = None
        self.strategy_engine = None
        self.is_running = False
        self.start_time = None
        
        # Simple statistics tracking
        self.stats = {
            'total_signals': 0,
            'signals_by_strategy': {
                'aggressive_momentum_ignition': 0,
                'moderate_ema_crossover': 0,
                'conservative_trend_rider': 0
            },
            'last_signal_time': None,
            'errors_count': 0
        }
        
        self._initialize_components()
        self._setup_scheduler()
        self._setup_signal_handlers()
        
        logger.info("EnhancedTradingAlertBot initialized successfully")
    
    def _initialize_components(self) -> None:
        """Initialize all bot components."""
        try:
            # Initialize enhanced strategy engine
            self.strategy_engine = EnhancedStrategyEngine()
            logger.info("Enhanced strategy engine initialized")
            
            # Initialize Telegram bot only if not in test mode
            # if not (TEST_MODE and SKIP_TELEGRAM_IN_TEST):
            #     try:
            #         self.telegram_bot = TelegramBot()
            #         logger.info("Telegram bot initialized")
                    
            #         # Test Telegram connection (non-blocking)
            #         if self.telegram_bot.test_connection():
            #             logger.info("Telegram bot connection test completed")
            #         else:
            #             logger.warning("Telegram bot connection test failed, but continuing...")
                        
            #     except Exception as e:
            #         logger.warning(f"Telegram bot initialization failed: {e}")
            #         logger.info("Continuing in console-only mode")
            #         self.telegram_bot = None
            # else:
            #     logger.info("Running in test mode - Telegram bot skipped")
            #     self.telegram_bot = None
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def _setup_scheduler(self) -> None:
        """Set up the APScheduler with enhanced strategy scheduling."""
        try:
            self.scheduler = BackgroundScheduler()
            
            # Add jobs for each enabled strategy
            for strategy, enabled in ENABLED_PROFILES.items():
                if enabled:
                    interval_minutes = SCHEDULE_INTERVALS[strategy]
                    
                    # Create interval trigger
                    trigger = IntervalTrigger(minutes=interval_minutes)
                    
                    # Add job to scheduler with strategy-specific function
                    if strategy == 'aggressive_momentum_ignition':
                        self.scheduler.add_job(
                            self._check_aggressive_strategy,
                            trigger=trigger,
                            id=f'check_{strategy}',
                            name=f'Check {strategy}',
                            max_instances=1,
                            coalesce=True
                        )
                    elif strategy == 'moderate_ema_crossover':
                        self.scheduler.add_job(
                            self._check_moderate_strategy,
                            trigger=trigger,
                            id=f'check_{strategy}',
                            name=f'Check {strategy}',
                            max_instances=1,
                            coalesce=True
                        )
                    elif strategy == 'conservative_trend_rider':
                        self.scheduler.add_job(
                            self._check_conservative_strategy,
                            trigger=trigger,
                            id=f'check_{strategy}',
                            name=f'Check {strategy}',
                            max_instances=1,
                            coalesce=True
                        )
                    
                    logger.info(f"Scheduled {strategy} to run every {interval_minutes} minutes")
            
            # Add daily summary job
            self.scheduler.add_job(
                self._send_daily_summary,
                CronTrigger(hour=0, minute=0),  # Daily at midnight UTC
                id='daily_summary',
                name='Daily Summary',
                max_instances=1
            )
            
            # Add health check job (every 6 hours)
            self.scheduler.add_job(
                self._health_check,
                IntervalTrigger(hours=6),
                id='health_check',
                name='Health Check',
                max_instances=1
            )
            
            # Add minute-by-minute status update for testing
            self.scheduler.add_job(
                self._minute_status_update,
                IntervalTrigger(minutes=1),
                id='minute_status',
                name='Minute Status Update',
                max_instances=1
            )
            
            logger.info("Scheduler setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup scheduler: {e}")
            raise
    
    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        logger.info("Signal handlers configured")
    
    def _signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def _check_aggressive_strategy(self) -> None:
        """Check aggressive momentum ignition strategy for all trading pairs."""
        try:
            logger.debug("Checking aggressive momentum ignition strategy...")
            
            for pair in TRADING_PAIRS:
                try:
                    signal = self.strategy_engine.check_aggressive_momentum_ignition(pair)
                    if signal:
                        self._process_trading_signal(signal)
                except Exception as e:
                    logger.error(f"Error checking aggressive strategy for {pair}: {e}")
                    self.stats['errors_count'] += 1
            
        except Exception as e:
            logger.error(f"Error in aggressive strategy check: {e}")
            self.stats['errors_count'] += 1
    
    def _check_moderate_strategy(self) -> None:
        """Check moderate EMA crossover strategy for all trading pairs."""
        try:
            logger.debug("Checking moderate EMA crossover strategy...")
            
            for pair in TRADING_PAIRS:
                try:
                    signal = self.strategy_engine.check_moderate_ema_crossover(pair)
                    if signal:
                        self._process_trading_signal(signal)
                except Exception as e:
                    logger.error(f"Error checking moderate strategy for {pair}: {e}")
                    self.stats['errors_count'] += 1
            
        except Exception as e:
            logger.error(f"Error in moderate strategy check: {e}")
            self.stats['errors_count'] += 1
    
    def _check_conservative_strategy(self) -> None:
        """Check conservative trend rider strategy for all trading pairs."""
        try:
            logger.debug("Checking conservative trend rider strategy...")
            
            for pair in TRADING_PAIRS:
                try:
                    signal = self.strategy_engine.check_conservative_trend_rider(pair)
                    if signal:
                        self._process_trading_signal(signal)
                except Exception as e:
                    logger.error(f"Error checking conservative strategy for {pair}: {e}")
                    self.stats['errors_count'] += 1
            
        except Exception as e:
            logger.error(f"Error in conservative strategy check: {e}")
            self.stats['errors_count'] += 1
    
    def _process_trading_signal(self, signal: Dict[str, Any]) -> None:
        """Process a trading signal and send alert."""
        try:
            # Update statistics
            self.stats['total_signals'] += 1
            strategy_name = signal.get('profile', 'unknown').lower().replace(' ', '_')
            if strategy_name in self.stats['signals_by_strategy']:
                self.stats['signals_by_strategy'][strategy_name] += 1
            
            self.stats['last_signal_time'] = datetime.now()
            
            # Log the signal
            logger.info(f"Trading signal generated: {signal['signal_type'].upper()} {signal['symbol']} "
                       f"at ${signal['price']:.2f} using {signal['strategy']}")
            
            # Send Telegram alert or console output
            # if self.telegram_bot:
            #     try:
            #         # Format the enhanced alert message
            #         alert_message = self._format_enhanced_alert(signal)
                    
            #         # Send the alert
            #         if self.telegram_bot.send_message(alert_message):
            #             logger.info(f"Alert sent successfully for {signal['symbol']}")
            #         else:
            #             logger.error(f"Failed to send alert for {signal['symbol']}")
                        
            #     except Exception as e:
            #         logger.error(f"Error sending Telegram alert: {e}")
            #         self.stats['errors_count'] += 1
            # else:
                # Console output for test mode
            console_message = self._format_console_alert(signal)
            print(f"\n{'='*60}")
            print(console_message)
            print(f"{'='*60}\n")
            logger.info(f"Console alert displayed for {signal['symbol']}")
            
            # Signal processed successfully
            
        except Exception as e:
            logger.error(f"Error processing trading signal: {e}")
            self.stats['errors_count'] += 1
    
    def _format_enhanced_alert(self, signal: Dict[str, Any]) -> str:
        """Format a simple trading alert message."""
        try:
            # Get strategy emoji and risk level
            strategy_info = {
                'Aggressive Momentum Ignition': ('🚨', 'HIGH RISK'),
                'Moderate EMA Crossover': ('⚖️', 'MEDIUM RISK'),
                'Conservative Trend Rider': ('🛡️', 'LOW RISK')
            }.get(signal['profile'], ('📊', 'UNKNOWN'))
            
            strategy_emoji, risk_level = strategy_info
            
            # Get signal emoji
            signal_emoji = '🟢' if signal['signal_type'] == 'long' else '🔴'
            
            # Simple alert format
            alert = f"{strategy_emoji} <b>TRADING SIGNAL</b> {signal_emoji}\n\n"
            alert += f"<b>Action:</b> {signal['signal_type'].upper()}\n"
            alert += f"<b>Asset:</b> {signal['symbol']}\n"
            alert += f"<b>Strategy:</b> {signal['profile']}\n"
            alert += f"<b>Risk Level:</b> {risk_level}\n"
            alert += f"<b>Timeframe:</b> {signal['timeframe']}\n\n"
            
            alert += f"<b>Entry:</b> ${signal['price']:,.2f}\n"
            alert += f"<b>Stop Loss:</b> ${signal['stop_loss']:,.2f}\n"
            alert += f"<b>Take Profit:</b> ${signal['take_profit']:,.2f}\n\n"
            
            # Add timestamp
            timestamp = signal.get('timestamp', datetime.now())
            if isinstance(timestamp, datetime):
                alert += f"<b>Time:</b> {timestamp.strftime('%H:%M UTC')}\n"
            
            return alert
            
        except Exception as e:
            logger.error(f"Error formatting alert: {e}")
            return f"🚨 {signal.get('signal_type', 'UNKNOWN')} {signal.get('symbol', 'UNKNOWN')}"
    
    def _format_console_alert(self, signal: Dict[str, Any]) -> str:
        """Format a simple trading alert message for console output."""
        try:
            # Get strategy emoji and risk level
            strategy_info = {
                'Aggressive Momentum Ignition': ('🚨', 'HIGH RISK'),
                'Moderate EMA Crossover': ('⚖️', 'MEDIUM RISK'),
                'Conservative Trend Rider': ('🛡️', 'LOW RISK')
            }.get(signal['profile'], ('📊', 'UNKNOWN'))
            
            strategy_emoji, risk_level = strategy_info
            
            # Get signal emoji
            signal_emoji = '🟢' if signal['signal_type'] == 'long' else '🔴'
            
            # Simple alert format
            alert = f"{strategy_emoji} TRADING SIGNAL {signal_emoji}\n"
            alert += f"Action: {signal['signal_type'].upper()}\n"
            alert += f"Asset: {signal['symbol']}\n"
            alert += f"Strategy: {signal['profile']}\n"
            alert += f"Risk Level: {risk_level}\n"
            alert += f"Timeframe: {signal['timeframe']}\n\n"
            
            alert += f"Entry: ${signal['price']:,.2f}\n"
            alert += f"Stop Loss: ${signal['stop_loss']:,.2f}\n"
            alert += f"Take Profit: ${signal['take_profit']:,.2f}\n\n"
            
            # Add timestamp
            timestamp = signal.get('timestamp', datetime.now())
            if isinstance(timestamp, datetime):
                alert += f"Time: {timestamp.strftime('%H:%M UTC')}\n"
            
            return alert
            
        except Exception as e:
            logger.error(f"Error formatting console alert: {e}")
            return f"🚨 {signal.get('signal_type', 'UNKNOWN')} {signal.get('symbol', 'UNKNOWN')}"
    

    
    def _send_daily_summary(self) -> None:
        """Send daily summary of trading activity."""
        try:
            # Calculate daily statistics
            today = datetime.now().date()
            daily_signals = sum(self.stats['signals_by_strategy'].values())
            
            # Format daily summary
            summary = f"📊 DAILY TRADING SUMMARY\n\n"
            summary += f"Date: {today.strftime('%Y-%m-%d')}\n"
            summary += f"Total Signals: {daily_signals}\n\n"
            
            summary += "Signals by Strategy:\n"
            for strategy, count in self.stats['signals_by_strategy'].items():
                strategy_name = strategy.replace('_', ' ').title()
                summary += f"  {strategy_name}: {count}\n"
            
            summary += f"\nErrors: {self.stats['errors_count']}\n"
            
            # Send summary via Telegram or console
            # if self.telegram_bot:
            #     telegram_summary = f"📊 <b>DAILY TRADING SUMMARY</b>\n\n"
            #     telegram_summary += f"<b>Date:</b> {today.strftime('%Y-%m-%d')}\n"
            #     telegram_summary += f"<b>Total Signals:</b> {daily_signals}\n\n"
                
            #     telegram_summary += "<b>Signals by Strategy:</b>\n"
            #     for strategy, count in self.stats['signals_by_strategy'].items():
            #         strategy_name = strategy.replace('_', ' ').title()
            #         telegram_summary += f"  {strategy_name}: {count}\n"
                
            #     telegram_summary += f"\n<b>Errors:</b> {self.stats['errors_count']}\n"
                
            #     self.telegram_bot.send_message(telegram_summary)
            #     logger.info("Daily summary sent via Telegram")
            # else:
            print(f"\n{'='*60}")
            print(summary)
            print(f"{'='*60}\n")
            logger.info("Daily summary displayed in console")
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
    
    def _health_check(self) -> None:
        """Perform health check and send status update."""
        try:
            # Calculate uptime
            if self.start_time:
                uptime = datetime.now() - self.start_time
                uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            else:
                uptime_str = "Unknown"
            
            # Format health check message
            health_msg = f"🏥 BOT HEALTH CHECK\n\n"
            health_msg += f"Status: {'🟢 RUNNING' if self.is_running else '🔴 STOPPED'}\n"
            health_msg += f"Uptime: {uptime_str}\n"
            health_msg += f"Total Signals: {self.stats['total_signals']}\n"
            health_msg += f"Errors: {self.stats['errors_count']}\n"
            health_msg += f"Last Signal: {self.stats['last_signal_time'] or 'None'}\n"
            
            # Send health check via Telegram or console
            # if self.telegram_bot:
            #     telegram_health = f"🏥 <b>BOT HEALTH CHECK</b>\n\n"
            #     telegram_health += f"<b>Status:</b> {'🟢 RUNNING' if self.is_running else '🔴 STOPPED'}\n"
            #     telegram_health += f"<b>Uptime:</b> {uptime_str}\n"
            #     telegram_health += f"<b>Total Signals:</b> {self.stats['total_signals']}\n"
            #     telegram_health += f"<b>Errors:</b> {self.stats['errors_count']}\n"
            #     telegram_health += f"<b>Last Signal:</b> {self.stats['last_signal_time'] or 'None'}\n"
                
            #     self.telegram_bot.send_message(telegram_health)
            #     logger.info("Health check sent via Telegram")
            # else:
            print(f"\n{'='*60}")
            print(health_msg)
            print(f"{'='*60}\n")
            logger.info("Health check displayed in console")
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
    
    def _minute_status_update(self) -> None:
        """Send minute-by-minute status update for testing and monitoring."""
        try:
            # Calculate uptime
            if self.start_time:
                uptime = datetime.now() - self.start_time
                uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            else:
                uptime_str = "Unknown"
            
            # Format minute status message
            status_msg = f"⏰ MINUTE STATUS UPDATE\n\n"
            status_msg += f"Status: {'🟢 RUNNING' if self.is_running else '🔴 STOPPED'}\n"
            status_msg += f"Uptime: {uptime_str}\n"
            status_msg += f"Total Signals: {self.stats['total_signals']}\n"
            status_msg += f"Errors: {self.stats['errors_count']}\n"
            status_msg += f"Last Signal: {self.stats['last_signal_time'] or 'None'}\n"
            status_msg += f"Active Jobs: {len(self.scheduler.get_jobs()) if self.scheduler else 0}\n"
            status_msg += f"Time: {datetime.now().strftime('%H:%M:%S UTC')}"
            
            # Send status via Telegram or console
            # if self.telegram_bot:
            #     telegram_status = f"⏰ <b>MINUTE STATUS UPDATE</b>\n\n"
            #     telegram_status += f"<b>Status:</b> {'🟢 RUNNING' if self.is_running else '🔴 STOPPED'}\n"
            #     telegram_status += f"<b>Uptime:</b> {uptime_str}\n"
            #     telegram_status += f"<b>Total Signals:</b> {self.stats['total_signals']}\n"
            #     telegram_status += f"<b>Errors:</b> {self.stats['errors_count']}\n"
            #     telegram_status += f"<b>Last Signal:</b> {self.stats['last_signal_time'] or 'None'}\n"
            #     telegram_status += f"<b>Active Jobs:</b> {len(self.scheduler.get_jobs()) if self.scheduler else 0}\n"
            #     telegram_status += f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S UTC')}"
                
            #     self.telegram_bot.send_message(telegram_status)
            #     logger.debug("Minute status update sent via Telegram")
            # else:
            print(f"\n{'='*60}")
            print(status_msg)
            print(f"{'='*60}\n")
            logger.debug("Minute status update displayed in console")
            
        except Exception as e:
            logger.error(f"Error in minute status update: {e}")
    
    def start(self) -> None:
        """Start the enhanced trading alert bot."""
        try:
            if self.is_running:
                logger.warning("Bot is already running")
                return
            
            logger.info("Starting Enhanced Trading Alert Bot...")
            
            # Start scheduler
            if self.scheduler:
                self.scheduler.start()
                logger.info("Scheduler started")
            
            # Send startup notification
            startup_msg = "🚀 ENHANCED TRADING BOT STARTED\n\n"
            startup_msg += "The bot is now running with enhanced strategies:\n"
            startup_msg += "• 🚨 Aggressive Momentum Ignition (5m)\n"
            startup_msg += "• ⚖️ Moderate EMA Crossover (15m)\n"
            startup_msg += "• 🛡️ Conservative Trend Rider (4h)\n\n"
            startup_msg += "Risk management and position sizing are active.\n"
            startup_msg += f"Monitoring {len(TRADING_PAIRS)} trading pairs.\n\n"
            startup_msg += "💻 CONSOLE ALERTS: ENABLED\n"
            startup_msg += "⏰ MINUTE STATUS UPDATES: ACTIVE (for testing)\n"
            startup_msg += "🔒 DRY RUN MODE: ENABLED (safe testing)\n"
            startup_msg += "📊 CLEAN & SIMPLE: No external dependencies"
            
            # if self.telegram_bot:
            #     telegram_startup = "🚀 <b>ENHANCED TRADING BOT STARTED</b>\n\n"
            #     telegram_startup += "The bot is now running with enhanced strategies:\n"
            #     telegram_startup += "• 🚨 Aggressive Momentum Ignition (5m)\n"
            #     telegram_startup += "• ⚖️ Moderate EMA Crossover (15m)\n"
            #     telegram_startup += "• 🛡️ Conservative Trend Rider (4h)\n\n"
            #     telegram_startup += "Risk management and position sizing are active.\n"
            #     telegram_startup += f"Monitoring {len(TRADING_PAIRS)} trading pairs.\n\n"
            #     telegram_startup += "📱 <b>TELEGRAM ALERTS: ENABLED</b>\n"
            #     telegram_startup += "⏰ <b>MINUTE STATUS UPDATES: ACTIVE</b> (for testing)\n"
            #     telegram_startup += "🔒 <b>DRY RUN MODE: ENABLED</b> (safe testing)"
                
            #     self.telegram_bot.send_message(telegram_startup)
            #     logger.info("Startup notification sent via Telegram")
            # else:
            print(f"\n{'='*60}")
            print(startup_msg)
            print(f"{'='*60}\n")
            logger.info("Startup notification displayed in console")
            
            self.is_running = True
            self.start_time = datetime.now()
            
            logger.info("Enhanced Trading Alert Bot started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise
    
    def stop(self) -> None:
        """Stop the enhanced trading alert bot."""
        try:
            if not self.is_running:
                logger.warning("Bot is not running")
                return
            
            logger.info("Stopping Enhanced Trading Alert Bot...")
            
            # Stop scheduler
            if self.scheduler:
                self.scheduler.shutdown()
                logger.info("Scheduler stopped")
            
            # Send shutdown notification
            shutdown_msg = "🛑 ENHANCED TRADING BOT STOPPED\n\n"
            shutdown_msg += "Bot has been shut down gracefully.\n"
            shutdown_msg += f"Total signals generated: {self.stats['total_signals']}"
            
            # if self.telegram_bot:
            #     telegram_shutdown = "🛑 <b>ENHANCED TRADING BOT STOPPED</b>\n\n"
            #     telegram_shutdown += "Bot has been shut down gracefully.\n"
            #     telegram_shutdown += f"Total signals generated: {self.stats['total_signals']}"
                
            #     self.telegram_bot.send_message(telegram_shutdown)
            #     logger.info("Shutdown notification sent via Telegram")
            # else:
            print(f"\n{'='*60}")
            print(shutdown_msg)
            print(f"{'='*60}\n")
            logger.info("Shutdown notification displayed in console")
            
            self.is_running = False
            
            # Cleanup
            self._cleanup()
            
            logger.info("Enhanced Trading Alert Bot stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop bot: {e}")
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self.strategy_engine:
                self.strategy_engine.cleanup()
            
            # if self.telegram_bot:
            #     self.telegram_bot.cleanup()
                
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status."""
        return {
            'is_running': self.is_running,
            'start_time': self.start_time,
            'uptime': str(datetime.now() - self.start_time) if self.start_time else '0:00:00',
            'stats': self.stats.copy(),
            'scheduler_running': self.scheduler.running if self.scheduler else False
        }


def main():
    """Main function to run the enhanced trading alert bot."""
    try:
        # Create and start the bot
        bot = EnhancedTradingAlertBot()
        
        # Start the bot
        bot.start()
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        
        # Stop the bot
        bot.stop()
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
