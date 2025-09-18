#!/usr/bin/env python3
"""
PythonAnywhere Task Script for Campus Connect Monitoring

This script is designed to run as a scheduled task on PythonAnywhere.
It performs monitoring and sends alerts if needed.

Author: Shivansh Ghelani
Version: 2.0 - PythonAnywhere Edition
"""

import os
import sys
import datetime
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import our modules
from keep_alive import RenderKeepAlive
from monitoring import ServiceMonitor
from reporting import ServiceReporter

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def run_monitoring_check():
    """Run a single monitoring check - perfect for PythonAnywhere scheduled tasks."""
    
    # Configuration
    service_name = os.getenv("SERVICE_NAME", "Campus Connect Backend")
    base_url = os.getenv("BASE_URL", "https://campusconnect-v2.onrender.com")
    
    print(f"🔍 Starting monitoring check for {service_name}")
    print(f"📡 Target URL: {base_url}")
    print(f"⏰ Time: {datetime.datetime.now().isoformat()}")
    
    # Initialize components
    keep_alive = RenderKeepAlive(
        base_url=base_url,
        endpoints=["/ping", "/api/health"],
        methods=["GET", "HEAD"],
        timeout=10
    )
    
    monitor = ServiceMonitor()
    reporter = ServiceReporter()
    
    try:
        # Perform health check
        results = keep_alive.ping_all_endpoints()
        
        # Log results
        healthy_endpoints = 0
        total_endpoints = len(results)
        
        for result in results:
            success = result.get("status") == "UP"
            if success:
                healthy_endpoints += 1
            
            # Log to monitoring system
            monitor.log_ping(
                endpoint=result["endpoint"],
                method=result["method"],
                status=200 if success else result.get("status_code", 500),
                response_time_ms=result.get("response_time_ms"),
                error=result.get("error") if not success else None,
                status_code=result.get("status_code")
            )
            
            # Print status
            status_icon = "✅" if success else "❌"
            response_time = result.get("response_time_ms", "N/A")
            print(f"  {status_icon} {result['method']} {result['endpoint']}: {response_time}ms")
        
        # Overall health assessment
        is_healthy = healthy_endpoints > 0
        health_percentage = (healthy_endpoints / total_endpoints) * 100
        
        print(f"📊 Health: {healthy_endpoints}/{total_endpoints} endpoints responding ({health_percentage:.1f}%)")
        
        # Send alert if service is completely down
        if not is_healthy:
            print("🚨 SERVICE DOWN - Sending immediate alert!")
            
            alert_data = {
                "alert_type": "DOWNTIME",
                "timestamp": datetime.datetime.now().isoformat(),
                "service_name": service_name,
                "service_url": base_url,
                "failed_endpoints": [r for r in results if r.get("status") != "UP"],
                "total_endpoints_checked": total_endpoints,
                "failed_count": total_endpoints - healthy_endpoints
            }
            
            success = reporter.send_alert(alert_data)
            if success:
                print("✅ Alert email sent successfully")
            else:
                print("❌ Failed to send alert email")
        else:
            print("✅ Service is healthy - no alerts needed")
        
        # Check if it's time for daily report (run this script once daily)
        now = datetime.datetime.now()
        if now.hour == 0:  # Midnight check
            print("🕛 Generating daily report...")
            
            # Generate report for past 24 hours
            end_time = now
            start_time = end_time - datetime.timedelta(days=1)
            report = monitor.generate_report(start_time=start_time, end_time=end_time)
            
            if report:
                success = reporter.send_report(report)
                if success:
                    print("📧 Daily report sent successfully")
                else:
                    print("❌ Failed to send daily report")
            else:
                print("⚠️ No data available for daily report")
        
        print(f"✅ Monitoring check completed at {datetime.datetime.now().isoformat()}")
        return True
        
    except Exception as e:
        print(f"❌ Error during monitoring: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🏥 Campus Connect Monitoring - PythonAnywhere Edition")
    print("=" * 60)
    
    success = run_monitoring_check()
    
    if success:
        print("🎉 Monitoring task completed successfully")
        sys.exit(0)
    else:
        print("💥 Monitoring task failed")
        sys.exit(1)