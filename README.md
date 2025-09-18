# � Campus Connect Monitoring - PythonAnywhere Edition

[![Python](https://img.shields.io/badge/python-3.9+-brightgreen.svg)](https://python.org)
[![PythonAnywhere](https://img.shields.io/badge/deploy-pythonanywhere-green.svg)](https://www.pythonanywhere.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A lightweight monitoring solution for Campus Connect backend service, optimized for PythonAnywhere deployment with immediate downtime alerts and daily reporting.

## ✨ Features

### 🚨 **Immediate Downtime Alerts**
- **Instant Email Notifications**: Alerts sent when Campus Connect goes down
- **Recovery Notifications**: Email when service comes back online
- **Color-coded Emails**: Red for downtime, green for recovery
- **Smart Detection**: Monitors multiple endpoints with different HTTP methods

### 📅 **Daily Reporting**  
- **Comprehensive Reports**: Daily uptime summaries with statistics
- **Incident Tracking**: Detailed downtime incident logs
- **Performance Metrics**: Response time analysis
- **HTML Email Reports**: Professional formatting with charts

### 🔄 **Reliable Monitoring**
- **Multiple Endpoints**: Monitors `/ping` and `/api/health`
- **HTTP Methods**: GET and HEAD requests for thorough checking
- **Smart Timeout**: 10-second timeout with proper error handling
- **Structured Logging**: JSON-based logs for easy analysis

### 🐍 **PythonAnywhere Optimized**
- **Scheduled Tasks**: Perfect for PythonAnywhere's task scheduler
- **Resource Efficient**: Optimized for free tier limitations
- **Simple Setup**: Upload files and configure one scheduled task
- **Zero Maintenance**: Runs automatically on PythonAnywhere

## 🚀 **Quick Setup (5 Minutes)**

### **1. Upload Files to PythonAnywhere**
Upload these essential files to your PythonAnywhere account:
- `keep_alive.py` - Core monitoring functionality
- `monitoring.py` - Data logging and analysis  
- `reporting.py` - Email alerts and reports
- `pythonanywhere_task.py` - **Main task script**
- `config.json` - Configuration settings
- `.env` - Your email credentials
- `requirements.txt` - Dependencies

### **2. Install Dependencies**
In PythonAnywhere Bash console:
```bash
cd ~/campusconnect-monitoring
pip3.10 install --user -r requirements.txt
```

### **3. Configure Email Settings**
Edit `.env` with your credentials:
```env
SERVICE_NAME="Campus Connect Backend"
BASE_URL="https://campusconnect-v2.onrender.com"
EMAIL_USER="your-email@gmail.com"
EMAIL_PASSWORD="your-gmail-app-password"
FROM_EMAIL="your-email@gmail.com"
RECIPIENT_EMAIL="alerts@example.com"
```

### **4. Create Scheduled Task**
1. Go to **Tasks** in PythonAnywhere dashboard
2. Create new task:
   - **Command**: `python3.10 /home/yourusername/campusconnect-monitoring/pythonanywhere_task.py`
   - **Schedule**: Hourly (for regular monitoring)
3. Save and activate

**That's it! Your monitoring is now active.** 🎉

## 📊 **What You Get**

### **Regular Health Checks**
- Monitors Campus Connect every hour (or your chosen frequency)
- Checks multiple endpoints with different HTTP methods
- Logs response times and status codes

### **Immediate Alerts** 
- Email sent instantly when service goes down
- Recovery notifications when service comes back
- Detailed incident information in alerts

### **Daily Reports**
- Comprehensive uptime statistics
- Average response times
- Downtime incident summaries
- Professional HTML email formatting

### **Local Logging**
- All activity logged to JSON files
- Historical data for analysis
- Automatic log rotation and retention

## 📋 **Essential Files**

```
campusconnect-monitoring/
├── pythonanywhere_task.py    # Main scheduled task script
├── keep_alive.py            # Core ping functionality
├── monitoring.py            # Data logging system
├── reporting.py             # Email alerts and reports
├── config.json              # Service configuration
├── .env                     # Email credentials (create this)
├── requirements.txt         # Python dependencies
└── logs/                    # Automatic log storage
    ├── monitoring.log       # System logs
    └── uptime_logs.json     # Monitoring data
```

## ⚙️ **Configuration**

### **Environment Variables (.env)**
```env
# Service Settings
SERVICE_NAME="Campus Connect Backend"
BASE_URL="https://campusconnect-v2.onrender.com"

# Email Settings (Gmail recommended)
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
EMAIL_USER="your-email@gmail.com"
EMAIL_PASSWORD="your-gmail-app-password"
FROM_EMAIL="your-email@gmail.com"
RECIPIENT_EMAIL="admin@example.com"
```

### **Service Configuration (config.json)**
```json
{
  "service_name": "Campus Connect Backend",
  "base_url": "https://campusconnect-v2.onrender.com",
  "endpoints": ["/ping", "/api/health"],
  "http_methods": ["GET", "HEAD"],
  "timeout_seconds": 10
}
```

## 🔧 **Testing**

Test your setup manually:
```bash
cd ~/campusconnect-monitoring
python3.10 pythonanywhere_task.py
```

Expected output:
```
🔍 Starting monitoring check for Campus Connect Backend
📡 Target URL: https://campusconnect-v2.onrender.com
  ✅ GET /ping: 180ms
  ✅ HEAD /ping: 165ms
  ✅ GET /api/health: 190ms
  ✅ HEAD /api/health: 175ms
📊 Health: 4/4 endpoints responding (100.0%)
✅ Service is healthy - no alerts needed
🎉 Monitoring task completed successfully
```

## 💰 **PythonAnywhere Free Tier**

**What's Included:**
- ✅ **1 scheduled task** (perfect for monitoring)
- ✅ **Python 3.10** support
- ✅ **Email sending** capabilities
- ✅ **File storage** for logs
- ✅ **Bash console** for setup

**Perfect for Campus Connect monitoring!**

## 📧 **Email Examples**

### **Downtime Alert**
```
Subject: 🚨 Campus Connect DOWNTIME Alert

Campus Connect Backend appears to be DOWN!
- Timestamp: 2025-09-18 13:45:00
- Failed Endpoints: /ping, /api/health
- All health checks failed
```

### **Daily Report**  
```
Subject: 📊 Campus Connect Daily Report

Service Status: Excellent (99.5% uptime)
- Total Checks: 24
- Successful: 23
- Failed: 1  
- Average Response Time: 185ms
```

## 🔍 **Troubleshooting**

**Task not running:**
- Check task logs in PythonAnywhere dashboard
- Verify file paths are correct
- Ensure Python version is 3.10

**Email not working:**
- Use Gmail App Password (not regular password)
- Verify SMTP settings in `.env`
- Check task output for error messages

**Import errors:**
- Install missing packages: `pip3.10 install --user package_name`
- Check requirements.txt is complete

## 📝 **Complete Setup Guide**

See [PYTHONANYWHERE_SETUP.md](PYTHONANYWHERE_SETUP.md) for detailed deployment instructions.

---

## 🎯 **Why PythonAnywhere?**

- ✅ **Free tier perfect** for monitoring tasks
- ✅ **Python-focused** hosting optimized for Python apps
- ✅ **Reliable scheduling** with built-in task management
- ✅ **Easy setup** - upload files and create one task
- ✅ **No server maintenance** - fully managed platform

**Perfect for Campus Connect monitoring with zero hosting costs!** 🚀

---

**Made with ❤️ by Shivansh Ghelani**

*Monitor Campus Connect reliably on PythonAnywhere!*

## ✨ Features

### 🚨 **NEW: Immediate Downtime Alerts**
- **Instant Notifications**: Email alerts sent the moment Campus Connect goes down
- **Recovery Alerts**: Notifications when service comes back online  
- **Color-coded Emails**: Red for downtime, green for recovery
- **No Delay**: Alerts sent within seconds of detection

### 📅 **NEW: Midnight-Only Reporting**  
- **Scheduled Reports**: Daily summaries sent only at 00:00 UTC
- **Smart Timing**: Prevents multiple daily reports
- **Comprehensive Stats**: 24-hour uptime analysis

### ☁️ **NEW: Vercel Serverless Deployment**
- **FastAPI Application**: Modern web interface with monitoring dashboard
- **Serverless Functions**: Automatic scaling and cost optimization
- **Cron Jobs**: Automated monitoring and reporting schedules
- **Web Dashboard**: Live monitoring interface with real-time status

### 🔄 Keep-Alive Service
- **Completion-based Timing**: Waits 60 seconds after ping completion
- **Multiple Endpoints**: Supports `/ping` and `/api/health` endpoints  
- **HTTP Methods**: GET and HEAD requests for flexibility
- **Smart Timeout**: 10-second timeout with proper error handling

### 📊 Monitoring & Logging
- **Comprehensive Logging**: Timestamp, status, response time, error details
- **Structured Data**: JSON-based log storage for easy analysis
- **Multiple Log Files**: Separate logs for keep-alive, monitoring, and reporting
- **Log Rotation**: Automatic daily rotation with 7-day retention

## � Deployment Options

### Option 1: Vercel Serverless (Recommended)

Deploy to Vercel for a modern serverless monitoring solution with web dashboard:

```bash
# Quick deployment
vercel --prod
```

**Features:**
- 🌐 Web dashboard at your Vercel URL
- ⚡ Serverless functions with automatic scaling
- 🔄 Automated cron jobs for monitoring
- 📧 Immediate alerts + midnight reports
- � Cost-effective (Vercel free tier)

**See [VERCEL_DEPLOY.md](VERCEL_DEPLOY.md) for complete deployment guide.**

### Option 2: Traditional Windows Service

Run as a continuous Windows service:

```batch
setup.bat
run_service.bat
```

## 📋 Requirements

### For Vercel Deployment
- **Vercel Account**
- **Gmail App Password** for email alerts
- **Python 3.12** (handled by Vercel)

### For Windows Service  
- **Python 3.9+**
- **Windows** with PowerShell support
- **Internet Connection**
- **SMTP Email Account**

## 🚀 Quick Start

### 1. Setup

Run the automated setup script:

```batch
setup.bat
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Create necessary directories
- Set up configuration files

### 2. Configuration

Edit the `.env` file with your settings:

```bash
# Service Configuration
SERVICE_NAME="Campus Connect Backend"
BASE_URL="https://your-app.onrender.com"

# Email Configuration (Gmail example)
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
EMAIL_USER="your-email@gmail.com"
EMAIL_PASSWORD="your-app-password"
FROM_EMAIL="your-email@gmail.com"
RECIPIENT_EMAIL="admin@example.com"
```

**⚠️ Security Note**: Use Gmail App Passwords, not your regular password!

### 3. Start Monitoring

Run the service:

```batch
run_service.bat
```

## ⚙️ Configuration Options

### config.json

```json
{
  "service_name": "Campus Connect Backend",
  "base_url": "https://your-render-service.onrender.com",
  "endpoints": ["/ping", "/api/health"],
  "http_methods": ["GET", "HEAD"],
  "interval_seconds": 60,
  "timeout_seconds": 10,
  "email": {
    "retry_count": 3,
    "retry_delay_seconds": 300
  },
  "reporting": {
    "schedule": "00:00",
    "reset_logs_after_send": true
  }
}
```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BASE_URL` | Your Render service URL | `https://myapp.onrender.com` |
| `SERVICE_NAME` | Display name for reports | `"My Backend API"` |
| `EMAIL_USER` | SMTP username | `user@gmail.com` |
| `EMAIL_PASSWORD` | SMTP password/app password | `your-app-password` |
| `RECIPIENT_EMAIL` | Report recipient | `admin@company.com` |

## 🔧 Command Line Usage

```bash
# Run the service normally
python main.py

# Use custom config file
python main.py --config my-config.json

# Generate and send report immediately (for testing)
python main.py --report-now
```

## 📊 Monitoring Dashboard

The service provides comprehensive monitoring through:

### Log Files
- `logs/main.log` - General service operations
- `logs/keep_alive.log` - Ping attempts and results  
- `logs/monitoring.log` - Monitoring system events
- `logs/reporting.log` - Email sending and backup operations

### Report Backups
- `logs/report_backups/` - Local JSON and HTML report copies
- Automatic backup even when email succeeds
- Timestamped filenames for easy organization

## 📈 Report Details

Daily reports include:

### 📋 Summary Statistics
- **Uptime Percentage**: Overall service availability
- **Total Checks**: Number of ping attempts
- **Successful/Failed Checks**: Breakdown of results
- **Average Response Time**: Performance metrics

### 🚨 Incident Details
- **Timestamp**: When each downtime occurred
- **Endpoint**: Which endpoint failed
- **HTTP Method**: GET/HEAD request type
- **Error Details**: Specific failure reason

### 🎨 Visual Indicators
- **Status Colors**: Green (Excellent), Yellow (Good), Orange (Fair), Red (Poor)
- **Professional Formatting**: HTML tables and styled layout
- **Service Information**: URL and configuration details

## 🔍 Troubleshooting

### Common Issues

**Service won't start**
- Check Python installation: `python --version`
- Verify virtual environment: Run `setup.bat` again
- Check `.env` file exists and is configured

**Email not sending**
- Verify SMTP settings in `.env`
- Use Gmail App Password (not regular password)
- Check firewall/network restrictions
- Look for detailed errors in `logs/reporting.log`

**Pings failing**
- Verify `BASE_URL` in `.env` is correct
- Test URL manually in browser
- Check if Render service is actually running
- Review `logs/keep_alive.log` for specific errors

### Debug Mode

Enable detailed logging by editing log level in the Python files:

```python
logger.add("logs/debug.log", level="DEBUG")
```

## 🔮 Future Enhancements

- **Multi-Service Support**: Monitor multiple Render services
- **Webhook Notifications**: Slack/Discord integration
- **Web Dashboard**: FastAPI-based monitoring interface
- **Database Storage**: PostgreSQL for long-term analytics
- **Alert Thresholds**: Custom downtime alert triggers

## 📝 File Structure

```
render-keep-alive/
├── main.py                 # Main service coordinator
├── keep_alive.py           # Ping functionality
├── monitoring.py           # Data collection and storage
├── reporting.py            # Email reports and backups
├── config.json            # Service configuration
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├── setup.bat             # Windows setup script
├── run_service.bat       # Windows service runner
└── logs/                 # All log files and backups
    ├── *.log             # Daily rotated logs
    └── report_backups/   # JSON/HTML report copies
```

## 📄 License

MIT License - feel free to use and modify for your projects.

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues and enhancement requests.

---

**Made with ❤️ by Shivansh Ghelani**

*Keep your Render services alive and monitored 24/7!*