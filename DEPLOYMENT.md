# 🚀 Deployment Guide for Trading Alert Bot

This guide will help you deploy your trading alert bot to various hosting platforms so it can run 24/7 without depending on your laptop.

## 📋 **Prerequisites**

1. **GitHub Repository**: Your code should be in a GitHub repo
2. **Environment Variables**: Set up your API keys and configuration
3. **Telegram Bot**: Create a Telegram bot and get the token

## 🔑 **Environment Variables Setup**

Create a `.env` file in your project root:

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Optional: Custom port
PORT=8080
```

## 🐳 **Option 1: Docker Deployment (Recommended)**

### **Local Testing with Docker**

```bash
# Build and run locally
docker-compose up --build

# Test the health endpoint
curl http://localhost:8080/health
```

### **Deploy to Any Platform with Docker**

1. **Build the image:**
   ```bash
   docker build -t trading-bot .
   ```

2. **Run on any VPS:**
   ```bash
   docker run -d \
     --name trading-bot \
     -p 8080:8080 \
     -e TELEGRAM_BOT_TOKEN=your_token \
     -e TELEGRAM_CHAT_ID=your_chat_id \
     --restart unless-stopped \
     trading-bot
   ```

## ☁️ **Option 2: Railway Deployment (Easiest)**

1. **Go to [Railway.app](https://railway.app)**
2. **Connect your GitHub account**
3. **Create new project from GitHub repo**
4. **Set environment variables:**
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
5. **Deploy** - Railway will auto-detect Python and deploy

## 🌐 **Option 3: Render Deployment**

1. **Go to [Render.com](https://render.com)**
2. **Create new Web Service**
3. **Connect your GitHub repo**
4. **Configure:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python service_runner.py`
   - **Environment Variables**: Set your Telegram credentials
5. **Deploy**

## 🦅 **Option 4: Heroku Deployment**

1. **Install Heroku CLI:**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Windows
   # Download from heroku.com
   ```

2. **Login and create app:**
   ```bash
   heroku login
   heroku create your-bot-name
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set TELEGRAM_BOT_TOKEN=your_token
   heroku config:set TELEGRAM_CHAT_ID=your_chat_id
   ```

4. **Deploy:**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

## 🖥️ **Option 5: VPS Deployment (Most Control)**

### **DigitalOcean/Linode Setup**

1. **Create Ubuntu VPS (1GB RAM minimum)**
2. **SSH into your server:**
   ```bash
   ssh root@your_server_ip
   ```

3. **Install dependencies:**
   ```bash
   # Update system
   apt update && apt upgrade -y
   
   # Install Python and pip
   apt install -y python3 python3-pip python3-venv
   
   # Install curl for health checks
   apt install -y curl
   ```

4. **Clone and setup your bot:**
   ```bash
   # Clone your repo
   git clone https://github.com/yourusername/trade-alert.git
   cd trade-alert
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

5. **Create systemd service:**
   ```bash
   sudo nano /etc/systemd/system/trading-bot.service
   ```

   Add this content:
   ```ini
   [Unit]
   Description=Trading Alert Bot
   After=network.target
   
   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/trade-alert
   Environment=PATH=/root/trade-alert/venv/bin
   Environment=TELEGRAM_BOT_TOKEN=your_token_here
   Environment=TELEGRAM_CHAT_ID=your_chat_id_here
   ExecStart=/root/trade-alert/venv/bin/python service_runner.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

6. **Start the service:**
   ```bash
   # Enable and start
   sudo systemctl enable trading-bot
   sudo systemctl start trading-bot
   
   # Check status
   sudo systemctl status trading-bot
   
   # View logs
   sudo journalctl -u trading-bot -f
   ```

## 🔍 **Monitoring Your Deployed Bot**

### **Health Check Endpoints**

- **Home**: `https://your-domain.com/`
- **Health**: `https://your-domain.com/health`

### **Check Bot Status**

```bash
# If using Docker
docker ps
docker logs trading-bot

# If using systemd
sudo systemctl status trading-bot
sudo journalctl -u trading-bot -f

# Health check
curl https://your-domain.com/health
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Bot not starting:**
   - Check environment variables
   - Verify Python version (3.8+)
   - Check logs for errors

2. **Telegram not working:**
   - Verify bot token and chat ID
   - Check if bot is added to chat
   - Test with simple message first

3. **Memory issues:**
   - Increase VPS RAM to 2GB
   - Check for memory leaks in logs
   - Restart service periodically

### **Logs and Debugging**

```bash
# View real-time logs
docker logs -f trading-bot

# Or for systemd
sudo journalctl -u trading-bot -f

# Check bot health
curl http://localhost:8080/health
```

## 💰 **Cost Comparison**

| Platform | Cost | Ease | Control |
|----------|------|------|---------|
| **Railway** | $5/month | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Render** | Free → $7/month | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Heroku** | $7/month | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **VPS** | $5-10/month | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Docker** | Varies | ⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🎯 **Recommended Path**

1. **Start with Railway** (easiest, good free tier)
2. **Move to VPS** if you need more control
3. **Use Docker** for consistency across platforms

## 🔒 **Security Notes**

- Never commit API keys to Git
- Use environment variables
- Consider using secrets management
- Regular security updates
- Monitor for unusual activity

## 📞 **Support**

- Check logs first
- Verify environment variables
- Test locally with Docker
- Check platform-specific documentation

---

**Happy Hosting! 🚀📈**
