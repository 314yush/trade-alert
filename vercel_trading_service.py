#!/usr/bin/env python3
"""
Vercel-Compatible Trading Alert Bot Service

This service is specifically designed for Vercel's serverless architecture
and can run the trading bot with Telegram integration.
"""

import os
import sys
import logging
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, request
import requests

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Global bot state
bot_state = {
    'is_running': False,
    'start_time': None,
    'total_signals': 0,
    'errors_count': 0,
    'last_signal_time': None,
    'telegram_bot': None,
    'trading_thread': None
}

class VercelTradingBot:
    """Trading bot adapted for Vercel's serverless environment."""
    
    def __init__(self):
        self.is_running = False
        self.start_time = None
        self.total_signals = 0
        self.errors_count = 0
        self.signals_history = []  # Store trading signals
        self.max_signals_stored = 100  # Keep last 100 signals
        
    def start(self):
        """Start the trading bot."""
        if self.is_running:
            return False, "Bot is already running"
        
        try:
            self.is_running = True
            self.start_time = datetime.now()
            self.total_signals = 0
            self.errors_count = 0
            
            # Start trading logic in background
            self._start_trading_logic()
            
            logger.info("Trading bot started successfully")
            return True, "Trading bot started successfully"
            
        except Exception as e:
            self.is_running = False
            self.errors_count += 1
            logger.error(f"Error starting trading bot: {e}")
            return False, f"Error starting bot: {str(e)}"
    
    def stop(self):
        """Stop the trading bot."""
        if not self.is_running:
            return False, "Bot is not running"
        
        try:
            self.is_running = False
            logger.info("Trading bot stopped")
            return True, "Trading bot stopped successfully"
            
        except Exception as e:
            self.errors_count += 1
            logger.error(f"Error stopping trading bot: {e}")
            return False, f"Error stopping bot: {str(e)}"
    
    def get_status(self):
        """Get current bot status."""
        if not self.start_time:
            uptime = "00:00:00"
        else:
            uptime_seconds = int((datetime.now() - self.start_time).total_seconds())
            hours, remainder = divmod(uptime_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        return {
            'bot_status': 'running' if self.is_running else 'stopped',
            'uptime': uptime,
            'total_signals': self.total_signals,
            'errors_count': self.errors_count,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'current_time': datetime.now().isoformat()
        }
    
    def get_signals(self, limit: int = 10):
        """Get the latest trading signals."""
        try:
            # Return the most recent signals (up to the limit)
            recent_signals = self.signals_history[-limit:] if self.signals_history else []
            
            return {
                'total_signals': self.total_signals,
                'signals_returned': len(recent_signals),
                'requested_limit': limit,
                'signals': recent_signals,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting signals: {e}")
            return {
                'error': f"Error retrieving signals: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def _add_signal_to_history(self, signal: dict):
        """Add a new signal to the history."""
        try:
            # Add timestamp if not present
            if 'timestamp' not in signal:
                signal['timestamp'] = datetime.now().isoformat()
            
            # Add to history
            self.signals_history.append(signal)
            
            # Keep only the last max_signals_stored signals
            if len(self.signals_history) > self.max_signals_stored:
                self.signals_history = self.signals_history[-self.max_signals_stored:]
                
            logger.info(f"Added signal to history: {signal.get('type', 'UNKNOWN')} {signal.get('symbol', 'UNKNOWN')}")
            
        except Exception as e:
            logger.error(f"Error adding signal to history: {e}")
    
    def _start_trading_logic(self):
        """Start the trading logic in a background thread."""
        def trading_loop():
            logger.info("Starting trading logic loop")
            while self.is_running:
                try:
                    # Simulate trading signal generation
                    if self._should_generate_signal():
                        self._generate_trading_signal()
                    
                    # Sleep for a bit to avoid overwhelming the system
                    time.sleep(30)  # Check every 30 seconds
                    
                except Exception as e:
                    self.errors_count += 1
                    logger.error(f"Error in trading loop: {e}")
                    time.sleep(60)  # Wait longer on error
        
        # Start trading thread
        self.trading_thread = threading.Thread(target=trading_loop, daemon=True)
        self.trading_thread.start()
        logger.info("Trading thread started")
    
    def _should_generate_signal(self):
        """Determine if we should generate a trading signal."""
        # Simple logic: generate signal every 5-15 minutes randomly
        import random
        return random.randint(1, 30) == 1  # 1 in 30 chance each 30 seconds
    
    def _generate_trading_signal(self):
        """Generate and send a trading signal."""
        try:
            # Create a sample trading signal
            signal = {
                'type': 'BUY' if self.total_signals % 2 == 0 else 'SELL',
                'symbol': 'BTC/USDT',
                'price': 45000 + (self.total_signals * 100),
                'timestamp': datetime.now().isoformat(),
                'confidence': 0.85,
                'reason': 'Momentum breakout detected',
                'strategy': 'Aggressive Momentum Ignition',
                'timeframe': '5m',
                'stop_loss': 45000 + (self.total_signals * 100) * 0.992,
                'take_profit': 45000 + (self.total_signals * 100) * 1.015,
                'leverage': 3,
                'risk_level': 'HIGH' if self.total_signals % 2 == 0 else 'MEDIUM'
            }
            
            # Add to signal history
            self._add_signal_to_history(signal)
            
            # Send via Telegram
            self._send_telegram_signal(signal)
            
            # Update stats
            self.total_signals += 1
            self.last_signal_time = datetime.now()
            
            logger.info(f"Generated trading signal: {signal['type']} {signal['symbol']}")
            
        except Exception as e:
            self.errors_count += 1
            logger.error(f"Error generating trading signal: {e}")
    
    def _send_telegram_signal(self, signal):
        """Send trading signal via Telegram."""
        try:
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            chat_id = os.getenv('TELEGRAM_CHAT_ID')
            
            if not bot_token or not chat_id:
                logger.warning("Telegram credentials not configured")
                return False
            
            # Format message
            message = f"""
🚨 **TRADING SIGNAL ALERT** 🚨

**Action**: {signal['type']}
**Symbol**: {signal['symbol']}
**Price**: ${signal['price']:,.2f}
**Confidence**: {signal['confidence']*100:.1f}%
**Time**: {signal['timestamp']}
**Reason**: {signal['reason']}

Generated by your Vercel Trading Bot 🤖
            """.strip()
            
            # Send via Telegram API
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                logger.info("Trading signal sent via Telegram successfully")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram signal: {e}")
            return False

def send_telegram_notification(message):
    """Send a notification message to Telegram."""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            logger.warning("Telegram credentials not configured for notifications")
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            logger.info("Telegram notification sent successfully")
            return True
        else:
            logger.error(f"Failed to send Telegram notification: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending Telegram notification: {e}")
        return False

# Initialize the trading bot
trading_bot = VercelTradingBot()

@app.route('/')
def home():
    """Home page."""
    return jsonify({
        'message': 'Vercel Trading Alert Bot Service',
        'status': 'running' if bot_state['is_running'] else 'stopped',
        'endpoints': {
            'health': '/health',
            'home': '/',
            'status': '/status',
            'signals': '/signals',
            'start': '/start',
            'stop': '/stop',
            'test': '/test'
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint."""
    uptime = "00:00:00"
    if bot_state['start_time']:
        uptime_seconds = int((datetime.now() - bot_state['start_time']).total_seconds())
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    return jsonify({
        'status': 'healthy',
        'bot_running': bot_state['is_running'],
        'uptime': uptime,
        'total_signals': bot_state['total_signals'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/status')
def status():
    """Bot status endpoint."""
    return jsonify(trading_bot.get_status())

@app.route('/signals')
def get_signals():
    """Get the latest trading signals."""
    try:
        # Get limit from query parameter, default to 10
        limit = request.args.get('limit', 10, type=int)
        
        # Validate limit (max 50 signals)
        if limit > 50:
            limit = 50
        elif limit < 1:
            limit = 1
        
        return jsonify(trading_bot.get_signals(limit=limit))
        
    except Exception as e:
        logger.error(f"Error in /signals endpoint: {e}")
        return jsonify({
            'error': f"Error retrieving signals: {str(e)}",
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/start')
def start_bot():
    """Start the trading bot."""
    success, message = trading_bot.start()
    if success:
        bot_state['is_running'] = True
        bot_state['start_time'] = trading_bot.start_time
        bot_state['total_signals'] = trading_bot.total_signals
        bot_state['errors_count'] = trading_bot.errors_count
        
        # Send Telegram notification
        notification = f"""
🚀 **TRADING BOT STARTED** 🚀

Your trading bot is now running and will generate signals automatically!

**Status**: ✅ Running
**Start Time**: {trading_bot.start_time.strftime('%Y-%m-%d %H:%M:%S')}
**Expected Signals**: Every 5-15 minutes

You'll receive trading alerts like this:
• BUY/SELL recommendations
• Price targets and confidence levels
• Market analysis and reasoning

Generated by your Vercel Trading Bot 🤖
        """.strip()
        
        send_telegram_notification(notification)
    
    return jsonify({
        'success': success,
        'message': message,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/stop')
def stop_bot():
    """Stop the trading bot."""
    success, message = trading_bot.stop()
    if success:
        bot_state['is_running'] = False
        
        # Send Telegram notification
        notification = f"""
⏹️ **TRADING BOT STOPPED** ⏹️

Your trading bot has been stopped and will no longer generate signals.

**Status**: ❌ Stopped
**Stop Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Signals Generated**: {bot_state['total_signals']}
**Total Errors**: {bot_state['errors_count']}

To restart the bot, visit:
`https://your-app.vercel.app/start`

Generated by your Vercel Trading Bot 🤖
        """.strip()
        
        send_telegram_notification(notification)
    
    return jsonify({
        'success': success,
        'message': message,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test')
def test():
    """Test endpoint for basic functionality."""
    # Send a test Telegram message
    test_message = f"""
🧪 **TELEGRAM INTEGRATION TEST** 🧪

This is a test message to verify your Telegram integration is working!

**Service Status**: ✅ Running
**Test Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Bot Status**: {'Running' if bot_state['is_running'] else 'Stopped'}

If you see this message, your Telegram bot is properly configured! 🎉

Generated by your Vercel Trading Bot 🤖
    """.strip()
    
    telegram_sent = send_telegram_notification(test_message)
    
    return jsonify({
        'message': 'Vercel Trading Service is working correctly!',
        'timestamp': datetime.now().isoformat(),
        'status': 'success',
        'bot_status': trading_bot.get_status(),
        'telegram_test_sent': telegram_sent
    })

# Vercel requires this for serverless deployment
app.debug = False

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting Vercel trading service on port {port}")
    logger.info("Available endpoints:")
    logger.info("  - / (home)")
    logger.info("  - /health (health check)")
    logger.info("  - /status (bot status)")
    logger.info("  - /signals (get trading signals)")
    logger.info("  - /start (start bot)")
    logger.info("  - /stop (stop bot)")
    logger.info("  - /test (test endpoint)")
    
    app.run(host='0.0.0.0', port=port, debug=False)
