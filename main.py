#!/usr/bin/env python3
"""
Main script for Render Service Keep-Alive & Monitoring

This script coordinates the keep-alive, monitoring, and reporting functionalities.
It can be run as a standalone script or scheduled via cron/systemd.

Author: Shivansh Ghelani
Version: 1.0
"""

import os
import time
import json
import threading
import datetime
import argparse
from loguru import logger
from dotenv import load_dotenv

# Import local modules
from keep_alive import RenderKeepAlive
from monitoring import ServiceMonitor
from reporting import ServiceReporter

# Load environment variables
load_dotenv()

# Configure logger
logger.add(
    "logs/main.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

class RenderServiceManager:
    """Main class for managing the Render service keep-alive and monitoring."""
    
    def __init__(self, config_path="config.json"):
        """Initialize the service manager."""
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Load configuration
        self.config = self._load_config(config_path)
        self.service_name = self.config.get("service_name", os.getenv("SERVICE_NAME", "Render Service"))
        self.base_url = self.config.get("base_url", os.getenv("BASE_URL", ""))
        self.reporting_schedule = self.config.get("reporting", {}).get("schedule", "00:00")
        self.reset_logs_after_send = self.config.get("reporting", {}).get("reset_logs_after_send", True)
        
        # Initialize components
        self.keep_alive = RenderKeepAlive(
            base_url=self.base_url,
            endpoints=self.config.get("endpoints", ["/ping", "/api/health"]),
            methods=self.config.get("http_methods", ["GET", "HEAD"]),
            timeout=self.config.get("timeout_seconds", 10)
        )
        self.monitor = ServiceMonitor()
        self.reporter = ServiceReporter(config_path)
        
        logger.info(f"Initialized RenderServiceManager for {self.service_name} at {self.base_url}")
    
    def _load_config(self, config_path):
        """Load configuration from JSON file."""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found. Using default values.")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file {config_path}. Using default values.")
            return {}
    
    def ping_service(self):
        """Ping the service and log the result using the keep-alive module."""
        results = self.keep_alive.ping_all_endpoints()
        
        # Track service health state
        healthy = any(result["status"] == "UP" for result in results)
        
        # Check if we need to send immediate downtime alert
        if not healthy and not hasattr(self, '_service_down_notified'):
            logger.warning("🚨 SERVICE DOWN DETECTED - Sending immediate alert!")
            self._send_immediate_downtime_alert(results)
            self._service_down_notified = True
        elif healthy and hasattr(self, '_service_down_notified'):
            # Service is back up - reset notification flag and send recovery alert
            logger.info("✅ SERVICE RECOVERED - Sending recovery notification!")
            self._send_service_recovery_alert(results)
            delattr(self, '_service_down_notified')
        
        # Log each result using the monitor
        for result in results:
            self.monitor.log_ping(
                result["endpoint"],
                result["method"], 
                result["status"],
                result["response_time_ms"],
                result.get("error"),
                result.get("status_code")
            )
        
        return results
    
    def _send_immediate_downtime_alert(self, results):
        """Send immediate email alert when service goes down."""
        try:
            failed_endpoints = [r for r in results if r["status"] == "DOWN"]
            
            alert_report = {
                "alert_type": "DOWNTIME",
                "timestamp": datetime.datetime.now().isoformat(),
                "service_name": self.service_name,
                "service_url": self.base_url,
                "failed_endpoints": failed_endpoints,
                "total_endpoints_checked": len(results),
                "failed_count": len(failed_endpoints)
            }
            
            # Send alert immediately
            success = self.reporter.send_alert(alert_report)
            if success:
                logger.info("📧 Immediate downtime alert sent successfully")
            else:
                logger.error("❌ Failed to send immediate downtime alert")
                
        except Exception as e:
            logger.error(f"Error sending downtime alert: {str(e)}")
    
    def _send_service_recovery_alert(self, results):
        """Send recovery notification when service comes back online."""
        try:
            recovery_report = {
                "alert_type": "RECOVERY",
                "timestamp": datetime.datetime.now().isoformat(),
                "service_name": self.service_name,
                "service_url": self.base_url,
                "recovery_endpoints": [r for r in results if r["status"] == "UP"],
                "message": "Service has recovered and is responding normally"
            }
            
            # Send recovery alert
            success = self.reporter.send_alert(recovery_report)
            if success:
                logger.info("📧 Service recovery alert sent successfully")
                
        except Exception as e:
            logger.error(f"Error sending recovery alert: {str(e)}")
    
    def run_keep_alive(self):
        """Run the keep-alive service continuously with completion-based timing."""
        logger.info(f"Starting keep-alive service for {self.base_url}")
        interval = self.config.get("interval_seconds", 60)
        
        while True:
            # Record start time for this cycle
            cycle_start = time.time()
            
            try:
                # Ping all endpoints
                results = self.ping_service()
                
                # Log cycle completion
                healthy = any(result["status"] == "UP" for result in results)
                logger.info(f"Ping cycle completed - Service {'healthy' if healthy else 'unhealthy'}")
                
            except Exception as e:
                logger.error(f"Error during ping cycle: {str(e)}")
            
            # Calculate how long the pings took
            cycle_duration = time.time() - cycle_start
            
            # Wait for the remainder of the interval (completion-based timing)
            sleep_time = max(0, interval - cycle_duration)
            
            if sleep_time > 0:
                logger.debug(f"Ping cycle took {cycle_duration:.2f}s, sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
            else:
                logger.warning(f"Ping cycle took {cycle_duration:.2f}s, longer than interval of {interval}s")
    
    def check_reporting_schedule(self):
        """Check if it's time to send a daily report - ONLY at midnight 00:00."""
        last_report_date = None
        
        while True:
            now = datetime.datetime.now()
            current_date = now.date()
            
            # Only send reports at exactly 00:00 (midnight)
            is_midnight = now.hour == 0 and now.minute == 0
            
            # Check if we should send a report
            should_send_report = (
                is_midnight and  # Must be exactly midnight
                last_report_date != current_date  # Haven't sent today's report yet
            )
            
            if should_send_report:
                logger.info("🕛 MIDNIGHT REPORT: Generating daily report at 00:00")
                
                # Generate report for the past 24 hours
                end_time = now
                start_time = end_time - datetime.timedelta(days=1)
                
                try:
                    report = self.monitor.generate_report(start_time=start_time, end_time=end_time)
                    
                    if report:
                        # Send the report
                        if self.reporter.send_report(report):
                            logger.info("📧 Daily midnight report sent successfully")
                            last_report_date = current_date
                            
                            # Reset logs if configured to do so
                            if self.reset_logs_after_send:
                                self.monitor.clear_logs()
                                logger.info("🗑️ Logs cleared after sending midnight report")
                        else:
                            logger.error("❌ Failed to send daily midnight report")
                    else:
                        logger.warning("⚠️ No data available for daily midnight report")
                        last_report_date = current_date  # Mark as attempted to avoid retries
                
                except Exception as e:
                    logger.error(f"Error generating daily midnight report: {str(e)}")
                
                # Sleep for 2 minutes to avoid multiple reports at midnight
                logger.info("⏳ Sleeping for 2 minutes after midnight report")
                time.sleep(120)  # 2 minutes
                
            else:
                # Check every 30 seconds, but only act at midnight
                time.sleep(30)
    
    def run(self):
        """Run the service manager with all components."""
        if not self.base_url:
            logger.error("Base URL is not configured. Please set it in config.json or .env file.")
            return
        
        # Start keep-alive thread
        keep_alive_thread = threading.Thread(target=self.run_keep_alive, daemon=True)
        keep_alive_thread.start()
        
        # Start reporting schedule thread
        reporting_thread = threading.Thread(target=self.check_reporting_schedule, daemon=True)
        reporting_thread.start()
        
        logger.info(f"Service manager started for {self.service_name} at {self.base_url}")
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Service manager stopped by user")
        except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Render Service Keep-Alive & Monitoring")
    parser.add_argument(
        "--config", 
        default="config.json", 
        help="Path to configuration file (default: config.json)"
    )
    parser.add_argument(
        "--report-now", 
        action="store_true", 
        help="Generate and send a report immediately"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    if args.report_now:
        # Generate and send a report immediately
        monitor = ServiceMonitor()
        reporter = ServiceReporter(args.config)
        
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        report = monitor.generate_report(start_time=yesterday, end_time=now)
        
        if report:
            if reporter.send_report(report):
                logger.info("Report sent successfully")
            else:
                logger.error("Failed to send report")
        else:
            logger.warning("No data available for report")
    else:
        # Run the service manager
        manager = RenderServiceManager(args.config)
        manager.run()