# 🐍 Campus Connect Monitoring - PythonAnywhere Deployment

## Quick Setup Guide for PythonAnywhere

### 📁 **Essential Files (Current Repository)**
- `main.py` - Main monitoring service (for continuous monitoring)  
- `keep_alive.py` - Core ping functionality
- `monitoring.py` - Logging and data storage
- `reporting.py` - Email alerts and reports
- `pythonanywhere_task.py` - **PythonAnywhere scheduled task** (NEW)
- `config.json` - Configuration settings
- `.env` - Environment variables (your email credentials)
- `requirements.txt` - Python dependencies

### 🚀 **PythonAnywhere Deployment Steps**

#### **1. Upload Files**
- Upload all Python files to your PythonAnywhere account
- Create a folder like `/home/yourusername/campusconnect-monitoring/`
- Upload the files to this folder

#### **2. Install Dependencies**
Open a **Bash console** on PythonAnywhere:
```bash
cd ~/campusconnect-monitoring
pip3.10 install --user -r requirements.txt
```

#### **3. Configure Environment Variables**
Edit your `.env` file with your email settings:
```bash
nano .env
```

Add your configuration:
```env
# Service Configuration
SERVICE_NAME="Campus Connect Backend"
BASE_URL="https://campusconnect-v2.onrender.com"

# Email Configuration  
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
EMAIL_USER="campusconnectldrp@gmail.com"
EMAIL_PASSWORD="vhmrdwekxmehrziu"
FROM_EMAIL="campusconnectldrp@gmail.com"
RECIPIENT_EMAIL="autobotmyra@gmail.com"
```

#### **4. Test the Monitoring**
Test manually first:
```bash
cd ~/campusconnect-monitoring
python3.10 pythonanywhere_task.py
```

You should see output like:
```
🔍 Starting monitoring check for Campus Connect Backend
📡 Target URL: https://campusconnect-v2.onrender.com
✅ GET /ping: 180ms
✅ HEAD /ping: 165ms
📊 Health: 4/4 endpoints responding (100.0%)
✅ Service is healthy - no alerts needed
🎉 Monitoring task completed successfully
```

#### **5. Setup Scheduled Task**
1. Go to **Tasks** in your PythonAnywhere dashboard
2. Click **"Create a new scheduled task"**
3. Configure:
   - **Command**: `python3.10 /home/yourusername/campusconnect-monitoring/pythonanywhere_task.py`
   - **Schedule**: `hourly` or `daily` (based on your needs)
   - **Description**: `Campus Connect Monitoring`

### 🎯 **PythonAnywhere Free Tier Limitations**
- **1 scheduled task** (perfect for monitoring)
- **Limited CPU seconds** per day
- **No always-on web apps** (but scheduled tasks work great!)

### ⚡ **Monitoring Options**

#### **Option A: Hourly Monitoring (Recommended)**
- Schedule: Every hour
- Command: `python3.10 ~/campusconnect-monitoring/pythonanywhere_task.py`
- **Pros**: Regular monitoring, immediate alerts within 1 hour
- **Cons**: Not real-time

#### **Option B: Daily Monitoring + Reports**
- Schedule: Once daily at midnight
- Same command as above
- **Pros**: Perfect for daily summaries
- **Cons**: Longer detection time for outages

### 📧 **What You Get**
- ✅ **Regular health checks** of Campus Connect
- ✅ **Immediate email alerts** when service goes down
- ✅ **Daily reports** with uptime statistics
- ✅ **Local logging** for historical data
- ✅ **Zero hosting costs** (PythonAnywhere free tier)

### 🔍 **Monitoring Output**
Each run will show:
```
============================================================
🏥 Campus Connect Monitoring - PythonAnywhere Edition  
============================================================
🔍 Starting monitoring check for Campus Connect Backend
📡 Target URL: https://campusconnect-v2.onrender.com
⏰ Time: 2025-09-18T13:45:00.123456
  ✅ GET /ping: 180ms
  ✅ HEAD /ping: 165ms  
  ✅ GET /api/health: 190ms
  ✅ HEAD /api/health: 175ms
📊 Health: 4/4 endpoints responding (100.0%)
✅ Service is healthy - no alerts needed
✅ Monitoring check completed at 2025-09-18T13:45:02.789012
🎉 Monitoring task completed successfully
```

### 🚨 **Alert Examples**

**Downtime Alert Email:**
- Subject: `🚨 Campus Connect DOWNTIME Alert`
- Immediate notification when service fails
- Details of which endpoints are down

**Daily Report Email:**
- Subject: `📊 Campus Connect Daily Report`
- Uptime percentage, response times
- Incident summary if any downtime occurred

### 🐛 **Troubleshooting**

**Task not running:**
- Check the task logs in PythonAnywhere dashboard
- Verify file paths are correct
- Ensure dependencies are installed

**Email not sending:**
- Verify Gmail App Password is correct  
- Check SMTP settings in `.env`
- Look at task output logs for errors

**Import errors:**
- Install missing packages: `pip3.10 install --user package_name`
- Check Python version compatibility

### 💡 **Pro Tips**
1. **Use Gmail App Passwords** for reliable email delivery
2. **Check task logs regularly** in PythonAnywhere dashboard  
3. **Test manually first** before setting up scheduled task
4. **Monitor your CPU seconds** usage in free tier

---

## 🎉 **Ready to Deploy!**

Your Campus Connect monitoring system is now optimized for PythonAnywhere. Upload the files, configure the scheduled task, and enjoy reliable monitoring with email alerts!

**Total setup time: ~15 minutes** ⏱️