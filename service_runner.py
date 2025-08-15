#!/usr/bin/env python3
"""
Service Runner for Trading Alert Bot

This module allows the bot to run as a background service on hosting platforms.
It handles graceful shutdowns and provides health check endpoints.
"""

import os
import sys
import time
import logging
from flask import Flask, jsonify
from threading import Thread
import signal

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_main import EnhancedTradingAlertBot

# Configure logging for service mode
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Flask app for health checks
app = Flask(__name__)

# Global bot instance
bot = None
bot_thread = None

@app.route('/health')
def health_check():
    """Health check endpoint for hosting platforms."""
    if bot and hasattr(bot, 'is_running') and bot.is_running:
        return jsonify({
            'status': 'healthy',
            'bot_running': True,
            'uptime': str(bot.get_uptime()) if hasattr(bot, 'get_uptime') else 'Unknown',
            'total_signals': bot.stats['total_signals'] if hasattr(bot, 'stats') else 0
        })
    else:
        return jsonify({
            'status': 'unhealthy',
            'bot_running': False
        }), 503

@app.route('/')
def home():
    """Simple home page."""
    return jsonify({
        'message': 'Trading Alert Bot Service',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'home': '/'
        }
    })

def run_bot():
    """Run the bot in a separate thread."""
    global bot
    try:
        logger.info("Initializing trading bot...")
        bot = EnhancedTradingAlertBot()
        
        logger.info("Starting trading bot...")
        bot.start()
        
        logger.info("Trading bot started successfully")
        
        # Keep the bot running
        while hasattr(bot, 'is_running') and bot.is_running:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Bot error: {e}")
        bot = None

def main():
    """Main service entry point."""
    global bot_thread
    
    logger.info("Starting Trading Alert Bot Service...")
    
    # Start bot in background thread
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 8080))
    
    logger.info(f"Starting service on port {port}")
    logger.info("Bot is starting in background...")
    logger.info("Service will be available at:")
    logger.info(f"  - Home: http://localhost:{port}/")
    logger.info(f"  - Health: http://localhost:{port}/health")
    
    # Run Flask app
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
        if bot:
            try:
                bot.stop()
            except:
                pass
        logger.info("Service shutdown complete")

if __name__ == '__main__':
    main()
