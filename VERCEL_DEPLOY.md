# Vercel Deployment Guide

## Overview
Deploy the Campus Connect monitoring system to Vercel as serverless functions with immediate downtime alerts and midnight-only reporting.

## Features
- ✅ **Immediate Alerts**: Sends email alerts the instant Campus Connect goes down
- ✅ **Recovery Notifications**: Alerts when service comes back online
- ✅ **Midnight Reports**: Daily uptime summary sent only at 00:00 UTC
- ✅ **Web Dashboard**: Live monitoring dashboard with service status
- ✅ **Serverless**: Runs on Vercel with automatic scaling
- ✅ **Cron Jobs**: Automated monitoring and reporting schedules

## Deployment Steps

### 1. Prerequisites
- Vercel account
- Gmail account with App Password
- Campus Connect service running at `https://campusconnect-v2.onrender.com`

### 2. Environment Configuration
Copy `.env.example` to `.env` and configure:

```bash
# Required Configuration
SERVICE_URL=https://campusconnect-v2.onrender.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SENDER_EMAIL=your-email@gmail.com
RECIPIENT_EMAILS=admin@example.com,alerts@example.com
```

### 3. Deploy to Vercel

#### Option A: CLI Deployment
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from project root
vercel --prod
```

#### Option B: GitHub Integration
1. Push code to GitHub repository
2. Connect repository to Vercel
3. Configure environment variables in Vercel dashboard
4. Deploy automatically

### 4. Environment Variables in Vercel
Add these in your Vercel project settings:

| Variable | Value | Required |
|----------|--------|----------|
| `SERVICE_URL` | `https://campusconnect-v2.onrender.com` | Yes |
| `SMTP_USERNAME` | Your Gmail address | Yes |
| `SMTP_PASSWORD` | Gmail App Password | Yes |
| `SENDER_EMAIL` | Your Gmail address | Yes |
| `RECIPIENT_EMAILS` | Alert email addresses (comma-separated) | Yes |
| `SERVICE_NAME` | `Campus Connect Backend` | No |
| `COMPANY_NAME` | `Campus Connect` | No |

### 5. Cron Jobs Configuration
The system uses Vercel Cron Jobs configured in `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/cron/ping",
      "schedule": "*/1 * * * *"
    },
    {
      "path": "/api/cron/report", 
      "schedule": "0 0 * * *"
    }
  ]
}
```

- **Ping Job**: Runs every minute to check service health
- **Report Job**: Runs daily at midnight UTC for summary reports

## API Endpoints

### Public Endpoints
- `GET /` - Web dashboard with live status
- `GET /api/health` - API health check
- `GET /api/ping` - Manual service ping test

### Monitoring Endpoints  
- `GET /api/logs` - Recent activity logs
- `GET /api/report` - Generate uptime report
- `POST /api/alert` - Test alert system

### Cron Endpoints (Internal)
- `GET /api/cron/ping` - Automated service monitoring
- `GET /api/cron/report` - Automated daily reporting

## Alert System

### Immediate Downtime Alerts
- Triggered instantly when Campus Connect goes down
- Email sent with red alert styling
- Includes downtime timestamp and affected endpoints

### Recovery Notifications
- Sent when service comes back online
- Green styling indicates recovery
- Shows downtime duration

### Daily Reports
- Sent only at midnight (00:00 UTC)
- Comprehensive uptime statistics
- Response time averages
- Incident summary

## Monitoring Dashboard

Access your deployed monitoring dashboard at:
```
https://your-project-name.vercel.app
```

Features:
- Live service status indicators
- Real-time response times
- Recent activity logs
- Manual test buttons
- Alert system testing

## Troubleshooting

### Common Issues

1. **Email Alerts Not Working**
   - Verify Gmail App Password is correct
   - Check SMTP credentials in environment variables
   - Test with `/api/alert` endpoint

2. **Cron Jobs Not Running**
   - Verify `vercel.json` cron configuration
   - Check Vercel dashboard for cron job status
   - Ensure endpoints return 200 status

3. **Service Monitoring Issues**
   - Confirm Campus Connect URL is accessible
   - Check timeout settings (default 10 seconds)
   - Review logs at `/api/logs` endpoint

### Log Analysis
- Check Vercel function logs in dashboard
- Use `/api/logs` endpoint for application logs
- Monitor response times and error patterns

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI development server
uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
```

Access local development at: `http://localhost:8000`

## Security Notes

- Never commit `.env` files to version control
- Use Gmail App Passwords instead of regular passwords
- Enable 2FA on your Gmail account
- Configure environment variables in Vercel dashboard
- Monitor alert email delivery for security incidents

## Support

For issues with the monitoring system:
- Check the web dashboard for service status
- Review API logs for error details  
- Test alert system with `/api/alert` endpoint
- Contact system administrator if alerts stop working