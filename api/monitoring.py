#!/usr/bin/env python3
"""
Monitoring module for Render Service Keep-Alive & Monitoring

This module handles the monitoring functionality, including logging ping attempts
and storing uptime/downtime data.

Author: Shivansh Ghelani
Version: 1.0
"""

import os
import json
import datetime
from loguru import logger

# Configure logger
logger.add(
    "logs/monitoring.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

class ServiceMonitor:
    """Class for monitoring service uptime and downtime."""
    
    def __init__(self, log_file="logs/uptime_logs.json"):
        """Initialize the service monitor."""
        self.log_file = log_file
        self.logs = self._load_logs()
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        logger.info(f"Initialized ServiceMonitor with log file: {self.log_file}")
    
    def _load_logs(self):
        """Load existing logs from file."""
        try:
            with open(self.log_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info(f"No existing logs found or invalid JSON. Starting with empty logs.")
            return []
    
    def _save_logs(self):
        """Save logs to file."""
        try:
            with open(self.log_file, "w") as f:
                json.dump(self.logs, f, indent=2)
            logger.debug(f"Saved {len(self.logs)} log entries to {self.log_file}")
        except Exception as e:
            logger.error(f"Failed to save logs to {self.log_file}: {str(e)}")
    
    def log_ping(self, endpoint, method, status, response_time_ms=None, error=None, status_code=None):
        """Log a ping attempt with its result."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "response_time_ms": response_time_ms,
            "status_code": status_code,
            "error": error
        }
        
        self.logs.append(log_entry)
        self._save_logs()
        
        # Log with appropriate level based on status
        if status == "UP":
            if response_time_ms:
                logger.info(f"✓ {method} {endpoint} is UP (HTTP {status_code}) - {response_time_ms}ms")
            else:
                logger.info(f"✓ {method} {endpoint} is UP")
        else:
            if error:
                logger.warning(f"✗ {method} {endpoint} is DOWN - {error}")
            else:
                logger.warning(f"✗ {method} {endpoint} is DOWN")
        
        return log_entry
    
    def get_logs(self, start_time=None, end_time=None):
        """Get logs within the specified time range."""
        if not start_time and not end_time:
            return self.logs
        
        filtered_logs = []
        for log in self.logs:
            log_time = datetime.datetime.fromisoformat(log["timestamp"])
            
            if start_time and log_time < start_time:
                continue
            
            if end_time and log_time > end_time:
                continue
            
            filtered_logs.append(log)
        
        return filtered_logs
    
    def generate_report(self, start_time=None, end_time=None):
        """Generate a report of uptime/downtime within the specified time range."""
        logs = self.get_logs(start_time, end_time)
        
        if not logs:
            logger.warning("No logs available for report generation")
            return None
        
        total_checks = len(logs)
        uptime_count = sum(1 for log in logs if log["status"] == "UP")
        downtime_count = total_checks - uptime_count
        
        # Get downtime incidents with detailed information
        downtime_incidents = []
        for log in logs:
            if log["status"] == "DOWN":
                incident = {
                    "timestamp": log["timestamp"],
                    "endpoint": log["endpoint"],
                    "method": log["method"],
                    "error": log.get("error", "Unknown error")
                }
                downtime_incidents.append(incident)
        
        # Calculate average response time for successful requests
        successful_pings = [log for log in logs if log["status"] == "UP" and log.get("response_time_ms")]
        avg_response_time = None
        if successful_pings:
            avg_response_time = sum(log["response_time_ms"] for log in successful_pings) / len(successful_pings)
        
        report = {
            "report_date": datetime.datetime.now().isoformat(),
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None,
            "total_checks": total_checks,
            "uptime_count": uptime_count,
            "downtime_count": downtime_count,
            "uptime_percentage": (uptime_count / total_checks) * 100 if total_checks > 0 else 0,
            "average_response_time_ms": round(avg_response_time, 2) if avg_response_time else None,
            "downtime_incidents": downtime_incidents
        }
        
        logger.info(f"Generated report: {total_checks} checks, {uptime_count} up, {downtime_count} down, "
                   f"{report['uptime_percentage']:.2f}% uptime")
        return report
    
    def clear_logs(self):
        """Clear all logs."""
        self.logs = []
        self._save_logs()
        logger.info("Cleared all logs")


if __name__ == "__main__":
    # Example usage
    monitor = ServiceMonitor()
    monitor.log_ping("/api/health", "GET", "UP", 150)
    monitor.log_ping("/ping", "GET", "UP", 120)
    report = monitor.generate_report()
    print(json.dumps(report, indent=2))