#!/usr/bin/env python3
"""
FastAPI application for Render Service Keep-Alive & Monitoring on Vercel

This provides a web API interface for the monitoring service, suitable for
serverless deployment on Vercel.

Author: Shivansh Ghelani
Version: 1.0
"""

import os
import json
import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import asyncio

# Import our monitoring modules
try:
    from keep_alive import RenderKeepAlive
    from monitoring import ServiceMonitor
    from reporting import ServiceReporter
except ImportError as e:
    print(f"Warning: Could not import monitoring modules: {e}")
    # Create stub classes for development
    class RenderKeepAlive:
        def __init__(self, **kwargs): pass
        def ping_all_endpoints(self): return []
    class ServiceMonitor:
        def __init__(self, **kwargs): pass
        def generate_report(self): return {}
        def get_recent_logs(self, n=10): return []
    class ServiceReporter:
        def __init__(self, **kwargs): pass
        def send_alert(self, data): pass

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not available, using os.environ directly")

app = FastAPI(
    title="Render Service Keep-Alive Monitor",
    description="Monitor and keep Render services alive with automated reporting",
    version="1.0.0"
)

# Global instances (will be initialized per request in serverless)
class MonitoringService:
    def __init__(self):
        # Load configuration from environment variables
        self.service_name = os.getenv("SERVICE_NAME", "Campus Connect Backend")
        self.base_url = os.getenv("BASE_URL", os.getenv("SERVICE_URL", "https://campusconnect-v2.onrender.com"))
        self.endpoints = ["/ping", "/api/health"]
        self.methods = ["GET", "HEAD"]
        self.timeout = 10
        
        # Email configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.email_user = os.getenv("EMAIL_USER", os.getenv("SMTP_USERNAME", ""))
        self.email_password = os.getenv("EMAIL_PASSWORD", os.getenv("SMTP_PASSWORD", ""))
        self.from_email = os.getenv("FROM_EMAIL", os.getenv("SENDER_EMAIL", ""))
        self.recipient_email = os.getenv("RECIPIENT_EMAIL", os.getenv("RECIPIENT_EMAILS", ""))
        
        # Initialize components
        self.keep_alive = RenderKeepAlive(
            base_url=self.base_url,
            endpoints=self.endpoints,
            methods=self.methods,
            timeout=self.timeout
        )
        self.monitor = ServiceMonitor()
        self.reporter = ServiceReporter()

# Pydantic models
class PingResponse(BaseModel):
    service_name: str
    base_url: str
    results: list
    healthy: bool
    timestamp: str

class ReportResponse(BaseModel):
    success: bool
    message: str
    report: Optional[dict] = None

class AlertResponse(BaseModel):
    success: bool
    message: str
    alert_sent: bool

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with service information."""
    html_content = f"""
    <html>
    <head>
        <title>Render Service Monitor</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .status {{ padding: 10px; border-radius: 5px; margin: 10px 0; }}
            .healthy {{ background-color: #d4edda; color: #155724; }}
            .unhealthy {{ background-color: #f8d7da; color: #721c24; }}
            .endpoint {{ background-color: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <h1>🚀 Render Service Keep-Alive Monitor</h1>
        <p>Monitoring service: <strong>{os.getenv("SERVICE_NAME", "Campus Connect Backend")}</strong></p>
        <p>Target URL: <strong>{os.getenv("BASE_URL", "Not configured")}</strong></p>
        
        <h2>Available Endpoints:</h2>
        <div class="endpoint"><strong>GET /ping</strong> - Test single ping to service</div>
        <div class="endpoint"><strong>GET /report</strong> - Generate current status report</div>
        <div class="endpoint"><strong>POST /alert</strong> - Send test alert email</div>
        <div class="endpoint"><strong>GET /health</strong> - API health check</div>
        <div class="endpoint"><strong>GET /logs</strong> - Recent monitoring logs</div>
        
        <h2>Quick Actions:</h2>
        <p><a href="/ping" style="background-color: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">🔍 Test Ping</a></p>
        <p><a href="/report" style="background-color: #28a745; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">📊 Generate Report</a></p>
        <p><a href="/logs" style="background-color: #6c757d; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">📋 View Logs</a></p>
        
        <hr>
        <p><em>This service prevents your Render app from going idle and provides monitoring alerts.</em></p>
    </body>
    </html>
    """
    return html_content

@app.get("/ping", response_model=PingResponse)
async def ping_service():
    """Ping the monitored service and return results."""
    try:
        service = MonitoringService()
        results = service.keep_alive.ping_all_endpoints()
        healthy = any(result["status"] == "UP" for result in results)
        
        # Log the results
        for result in results:
            service.monitor.log_ping(
                result["endpoint"],
                result["method"],
                result["status"],
                result["response_time_ms"],
                result.get("error"),
                result.get("status_code")
            )
        
        return PingResponse(
            service_name=service.service_name,
            base_url=service.base_url,
            results=results,
            healthy=healthy,
            timestamp=datetime.datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error pinging service: {str(e)}")

@app.get("/report", response_model=ReportResponse)
async def generate_report():
    """Generate and optionally send a monitoring report."""
    try:
        service = MonitoringService()
        
        # Generate report for the last 24 hours
        now = datetime.datetime.now()
        start_time = now - datetime.timedelta(days=1)
        report = service.monitor.generate_report(start_time=start_time, end_time=now)
        
        if report:
            # Save backup locally
            service.reporter._save_report_backup(report)
            
            return ReportResponse(
                success=True,
                message="Report generated successfully",
                report=report
            )
        else:
            return ReportResponse(
                success=False,
                message="No data available for report generation"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@app.post("/alert", response_model=AlertResponse)
async def send_test_alert(background_tasks: BackgroundTasks):
    """Send a test alert email."""
    try:
        service = MonitoringService()
        
        # Create test alert
        test_alert = {
            "alert_type": "TEST",
            "timestamp": datetime.datetime.now().isoformat(),
            "service_name": service.service_name,
            "service_url": service.base_url,
            "message": "This is a test alert to verify email functionality"
        }
        
        # Send alert in background
        def send_alert():
            service.reporter.send_alert(test_alert)
        
        background_tasks.add_task(send_alert)
        
        return AlertResponse(
            success=True,
            message="Test alert queued for sending",
            alert_sent=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending test alert: {str(e)}")

@app.get("/health")
async def health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": os.getenv("SERVICE_NAME", "Render Monitor"),
        "version": "1.0.0"
    }

@app.get("/logs")
async def get_recent_logs():
    """Get recent monitoring logs."""
    try:
        service = MonitoringService()
        
        # Get logs from the last 6 hours
        now = datetime.datetime.now()
        start_time = now - datetime.timedelta(hours=6)
        recent_logs = service.monitor.get_logs(start_time=start_time, end_time=now)
        
        return {
            "logs_count": len(recent_logs),
            "time_range": {
                "start": start_time.isoformat(),
                "end": now.isoformat()
            },
            "logs": recent_logs[-50:]  # Last 50 entries
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving logs: {str(e)}")

@app.get("/cron/midnight-report")
async def midnight_report_cron():
    """Cron endpoint for midnight reports (called by external scheduler)."""
    try:
        service = MonitoringService()
        
        # Generate report for the past 24 hours
        now = datetime.datetime.now()
        start_time = now - datetime.timedelta(days=1)
        report = service.monitor.generate_report(start_time=start_time, end_time=now)
        
        if report:
            success = service.reporter.send_report(report)
            if success:
                # Clear logs if configured
                service.monitor.clear_logs()
                return {"success": True, "message": "Midnight report sent successfully"}
            else:
                return {"success": False, "message": "Failed to send midnight report"}
        else:
            return {"success": False, "message": "No data available for midnight report"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in midnight report: {str(e)}")

@app.get("/cron/keep-alive")
async def keep_alive_cron():
    """Cron endpoint for keep-alive pings (called by external scheduler)."""
    try:
        service = MonitoringService()
        results = service.keep_alive.ping_all_endpoints()
        healthy = any(result["status"] == "UP" for result in results)
        
        # Log the results
        for result in results:
            service.monitor.log_ping(
                result["endpoint"],
                result["method"],
                result["status"],
                result["response_time_ms"],
                result.get("error"),
                result.get("status_code")
            )
        
        # Check for downtime and send immediate alert if needed
        if not healthy:
            failed_endpoints = [r for r in results if r["status"] == "DOWN"]
            alert_report = {
                "alert_type": "DOWNTIME",
                "timestamp": datetime.datetime.now().isoformat(),
                "service_name": service.service_name,
                "service_url": service.base_url,
                "failed_endpoints": failed_endpoints,
                "total_endpoints_checked": len(results),
                "failed_count": len(failed_endpoints)
            }
            service.reporter.send_alert(alert_report)
        
        return {
            "success": True,
            "healthy": healthy,
            "results": results,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in keep-alive cron: {str(e)}")

# Export app for Vercel
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)