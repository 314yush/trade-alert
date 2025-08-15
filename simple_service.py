#!/usr/bin/env python3
"""
Simple Service Runner for Trading Alert Bot

This is a simplified version for testing Railway deployment.
It provides the health endpoints without the complex bot initialization.
"""

import os
import logging
from flask import Flask, jsonify
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Simulate bot status
bot_status = {
    'is_running': True,
    'start_time': datetime.now(),
    'total_signals': 0,
    'errors_count': 0
}

@app.route('/')
def home():
    """Home page."""
    return jsonify({
        'message': 'Trading Alert Bot Service',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'home': '/',
            'status': '/status'
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'bot_running': bot_status['is_running'],
        'uptime': '00:05:30',
        'total_signals': bot_status['total_signals'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/status')
def status():
    """Bot status endpoint."""
    uptime = datetime.now() - bot_status['start_time']
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return jsonify({
        'bot_status': 'running',
        'uptime': f"{hours:02d}:{minutes:02d}:{seconds:02d}",
        'total_signals': bot_status['total_signals'],
        'errors_count': bot_status['errors_count'],
        'start_time': bot_status['start_time'].isoformat(),
        'current_time': datetime.now().isoformat()
    })

@app.route('/test')
def test():
    """Test endpoint for basic functionality."""
    return jsonify({
        'message': 'Service is working correctly!',
        'timestamp': datetime.now().isoformat(),
        'status': 'success'
    })

# Vercel requires this for serverless deployment
app.debug = False

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting simple service on port {port}")
    logger.info("Available endpoints:")
    logger.info("  - / (home)")
    logger.info("  - /health (health check)")
    logger.info("  - /status (bot status)")
    logger.info("  - /test (test endpoint)")
    
    app.run(host='0.0.0.0', port=port, debug=False)
