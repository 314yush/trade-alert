#!/bin/bash

# Quick Deploy Script for Trading Alert Bot
# This script helps you quickly deploy the bot on a VPS

echo "🚀 Trading Alert Bot - Quick Deploy Script"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
echo "🔧 Installing dependencies..."
apt install -y python3 python3-pip python3-venv git curl

# Create bot user
echo "👤 Creating bot user..."
useradd -m -s /bin/bash tradingbot
usermod -aG sudo tradingbot

# Switch to bot user directory
cd /home/tradingbot

# Clone repository (replace with your repo URL)
echo "📥 Cloning repository..."
git clone https://github.com/yourusername/trade-alert.git
cd trade-alert

# Create virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Create .env file
echo "🔑 Creating environment file..."
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
PORT=8080
EOF

# Set permissions
chown -R tradingbot:tradingbot /home/tradingbot/trade-alert

# Create systemd service
echo "⚙️ Creating system service..."
cat > /etc/systemd/system/trading-bot.service << EOF
[Unit]
Description=Trading Alert Bot
After=network.target

[Service]
Type=simple
User=tradingbot
WorkingDirectory=/home/tradingbot/trade-alert
Environment=PATH=/home/tradingbot/trade-alert/venv/bin
EnvironmentFile=/home/tradingbot/trade-alert/.env
ExecStart=/home/tradingbot/trade-alert/venv/bin/python service_runner.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "🚀 Starting bot service..."
systemctl daemon-reload
systemctl enable trading-bot
systemctl start trading-bot

# Wait a moment and check status
sleep 5
echo "📊 Service status:"
systemctl status trading-bot --no-pager

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔍 Check bot status:"
echo "   sudo systemctl status trading-bot"
echo ""
echo "📝 View logs:"
echo "   sudo journalctl -u trading-bot -f"
echo ""
echo "🌐 Health check:"
echo "   curl http://localhost:8080/health"
echo ""
echo "⚠️  Don't forget to:"
echo "   1. Update .env file with your Telegram credentials"
echo "   2. Restart the service: sudo systemctl restart trading-bot"
echo "   3. Check logs for any errors"
echo ""
echo "🎉 Your bot should now be running 24/7!"
