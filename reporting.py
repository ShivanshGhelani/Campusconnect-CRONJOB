#!/usr/bin/env python3
"""
Reporting module for Render Service Keep-Alive & Monitoring

This module handles the reporting functionality, including generating daily
reports and sending them via email.

Author: Shivansh Ghelani
Version: 1.0
"""

import os
import json
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logger
logger.add(
    "logs/reporting.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

class ServiceReporter:
    """Class for generating and sending service reports."""
    
    def __init__(self, config_path="config.json"):
        """Initialize the service reporter."""
        self.config = self._load_config(config_path)
        self.email_config = self.config.get("email", {})
        
        # Use .env values as fallback for email configuration
        self.smtp_server = self.email_config.get("smtp_server") or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(self.email_config.get("smtp_port") or os.getenv("SMTP_PORT", 587))
        self.smtp_username = self.email_config.get("smtp_username") or os.getenv("EMAIL_USER")
        self.smtp_password = self.email_config.get("smtp_password") or os.getenv("EMAIL_PASSWORD")
        self.sender_email = self.email_config.get("sender_email") or os.getenv("FROM_EMAIL")
        
        # Handle recipient emails - support both config and env
        config_recipients = self.email_config.get("recipient_emails", [])
        env_recipient = os.getenv("RECIPIENT_EMAIL")
        if config_recipients and config_recipients != ["admin@example.com"]:
            self.recipient_emails = config_recipients
        elif env_recipient:
            self.recipient_emails = [env_recipient]
        else:
            self.recipient_emails = config_recipients
            
        self.service_name = self.config.get("service_name", "Render Service")
        
        logger.info(f"Initialized ServiceReporter for {self.service_name}")
        logger.info(f"SMTP Server: {self.smtp_server}:{self.smtp_port}")
        logger.info(f"Recipients: {len(self.recipient_emails)} configured")
    
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
    
    def format_report_email(self, report):
        """Format the report data into an email body."""
        if not report:
            return "No report data available."
        
        uptime_percentage = report.get("uptime_percentage", 0)
        total_checks = report.get("total_checks", 0)
        uptime_count = report.get("uptime_count", 0)
        downtime_count = report.get("downtime_count", 0)
        avg_response_time = report.get("average_response_time_ms")
        
        # Format timestamps
        start_time = report.get('start_time', 'N/A')
        end_time = report.get('end_time', 'N/A')
        if start_time != 'N/A':
            start_time = datetime.datetime.fromisoformat(start_time).strftime("%Y-%m-%d %H:%M:%S")
        if end_time != 'N/A':
            end_time = datetime.datetime.fromisoformat(end_time).strftime("%Y-%m-%d %H:%M:%S")
        
        # Determine status and color
        if uptime_percentage >= 99:
            status = "Excellent"
            color = "#4CAF50"
        elif uptime_percentage >= 95:
            status = "Good"
            color = "#FFC107"
        elif uptime_percentage >= 90:
            status = "Fair"
            color = "#FF9800"
        else:
            status = "Poor"
            color = "#F44336"
        
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
            <h2 style="color: #333; border-bottom: 2px solid #ddd; padding-bottom: 10px;">
                {self.service_name} - Daily Uptime Report
            </h2>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Report Period:</strong> {start_time} to {end_time}</p>
                <p><strong>Generated:</strong> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <h3 style="color: #333;">📊 Summary Statistics</h3>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                <tr style="background-color: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Uptime Percentage</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd; color: {color}; font-weight: bold;">{uptime_percentage:.2f}%</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Total Checks</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{total_checks}</td>
                </tr>
                <tr style="background-color: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Successful Checks</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd; color: green;">{uptime_count}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Failed Checks</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd; color: red;">{downtime_count}</td>
                </tr>"""
        
        if avg_response_time:
            email_body += f"""
                <tr style="background-color: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Average Response Time</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{avg_response_time:.0f}ms</td>
                </tr>"""
        
        email_body += """
            </table>
            
            <div style="background-color: """ + color + """; 
                        color: white; 
                        padding: 15px; 
                        border-radius: 5px;
                        text-align: center;
                        margin: 20px 0;">
                <h3 style="margin: 0;">Service Status: """ + status + """</h3>
            </div>
        """
        
        # Add downtime details if there were any
        downtime_incidents = report.get("downtime_incidents", [])
        if downtime_incidents:
            email_body += """
            <h3 style="color: #333;">⚠️ Downtime Incidents</h3>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                <tr style="background-color: #ffebee;">
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Timestamp</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Endpoint</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Method</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Error</th>
                </tr>
            """
            
            for incident in downtime_incidents:
                timestamp = datetime.datetime.fromisoformat(incident["timestamp"]).strftime("%H:%M:%S")
                email_body += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{timestamp}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{incident['endpoint']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{incident['method']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: red;">{incident['error']}</td>
                </tr>
                """
            
            email_body += "</table>"
        else:
            email_body += """
            <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #2e7d2e; margin: 0;">✅ No downtime incidents recorded!</h3>
            </div>
            """
        
        email_body += """
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
            <p style="color: #666; font-size: 12px;">
                This report was automatically generated by the Render Service Keep-Alive & Monitoring system.<br>
                Service URL: """ + self.config.get("base_url", "Not configured") + """
            </p>
        </body>
        </html>
        """
        
        return email_body
    
    def send_report_email(self, report):
        """Send the report via email."""
        if not self.smtp_server or not self.smtp_username or not self.smtp_password:
            logger.error("SMTP configuration is incomplete. Cannot send email.")
            return False
        
        if not self.sender_email or not self.recipient_emails:
            logger.error("Sender or recipient email addresses are missing. Cannot send email.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"{self.service_name} - Daily Uptime Report"
            msg["From"] = self.sender_email
            msg["To"] = ", ".join(self.recipient_emails)
            
            # Attach HTML content
            html_content = self.format_report_email(report)
            msg.attach(MIMEText(html_content, "html"))
            
            # Connect to SMTP server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Successfully sent report email to {', '.join(self.recipient_emails)}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send report email: {str(e)}")
            return False
    
    def send_alert(self, alert_report):
        """Send immediate alert for service downtime or recovery."""
        # Always save alert locally first
        self._save_alert_backup(alert_report)
        
        # Send email alert
        return self.send_alert_email(alert_report)
    
    def send_alert_email(self, alert_report):
        """Send alert via email."""
        if not self.smtp_server or not self.smtp_username or not self.smtp_password:
            logger.error("SMTP configuration is incomplete. Cannot send alert email.")
            return False
        
        if not self.sender_email or not self.recipient_emails:
            logger.error("Sender or recipient email addresses are missing. Cannot send alert email.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            
            alert_type = alert_report.get("alert_type", "UNKNOWN")
            service_name = alert_report.get("service_name", self.service_name)
            
            if alert_type == "DOWNTIME":
                subject = f"🚨 ALERT: {service_name} is DOWN!"
                priority = "urgent"
            elif alert_type == "RECOVERY":
                subject = f"✅ RECOVERY: {service_name} is back online!"
                priority = "normal"
            else:
                subject = f"📊 {service_name} - Service Alert"
                priority = "normal"
            
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = ", ".join(self.recipient_emails)
            msg["X-Priority"] = "1" if priority == "urgent" else "3"  # High priority for downtime
            
            # Attach HTML content
            html_content = self.format_alert_email(alert_report)
            msg.attach(MIMEText(html_content, "html"))
            
            # Connect to SMTP server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Successfully sent {alert_type.lower()} alert email to {', '.join(self.recipient_emails)}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send alert email: {str(e)}")
            return False
    
    def format_alert_email(self, alert_report):
        """Format alert data into an email body."""
        alert_type = alert_report.get("alert_type", "UNKNOWN")
        service_name = alert_report.get("service_name", self.service_name)
        timestamp = alert_report.get("timestamp", "Unknown")
        service_url = alert_report.get("service_url", "Unknown")
        
        if alert_type == "DOWNTIME":
            status_color = "#F44336"  # Red
            status_text = "SERVICE DOWN"
            icon = "🚨"
            failed_endpoints = alert_report.get("failed_endpoints", [])
            
            email_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
                <div style="background-color: {status_color}; color: white; padding: 20px; text-align: center;">
                    <h1 style="margin: 0;">{icon} SERVICE DOWNTIME ALERT</h1>
                </div>
                
                <div style="padding: 20px;">
                    <h2 style="color: #333;">{service_name} is Currently DOWN</h2>
                    
                    <div style="background-color: #ffebee; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Alert Time:</strong> {timestamp}</p>
                        <p><strong>Service URL:</strong> {service_url}</p>
                        <p><strong>Status:</strong> <span style="color: red; font-weight: bold;">DOWN</span></p>
                    </div>
                    
                    <h3>Failed Endpoints:</h3>
                    <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                        <tr style="background-color: #ffebee;">
                            <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Endpoint</th>
                            <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Method</th>
                            <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Error</th>
                        </tr>
            """
            
            for endpoint in failed_endpoints:
                email_body += f"""
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd;">{endpoint.get('endpoint', 'N/A')}</td>
                            <td style="padding: 8px; border: 1px solid #ddd;">{endpoint.get('method', 'N/A')}</td>
                            <td style="padding: 8px; border: 1px solid #ddd; color: red;">{endpoint.get('error', 'Unknown error')}</td>
                        </tr>
                """
            
            email_body += """
                    </table>
                    
                    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px;">
                        <p><strong>⚠️ Action Required:</strong></p>
                        <p>Your service is currently unavailable. Please check your server logs and take immediate action to restore service.</p>
                    </div>
                </div>
            """
                
        elif alert_type == "RECOVERY":
            status_color = "#4CAF50"  # Green
            icon = "✅"
            
            email_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
                <div style="background-color: {status_color}; color: white; padding: 20px; text-align: center;">
                    <h1 style="margin: 0;">{icon} SERVICE RECOVERY NOTIFICATION</h1>
                </div>
                
                <div style="padding: 20px;">
                    <h2 style="color: #333;">{service_name} has Recovered</h2>
                    
                    <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Recovery Time:</strong> {timestamp}</p>
                        <p><strong>Service URL:</strong> {service_url}</p>
                        <p><strong>Status:</strong> <span style="color: green; font-weight: bold;">ONLINE</span></p>
                    </div>
                    
                    <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px;">
                        <p><strong>✅ Good News:</strong></p>
                        <p>Your service is now responding normally. Monitoring will continue automatically.</p>
                    </div>
                </div>
            """
        
        email_body += """
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="color: #666; font-size: 12px;">
                    This alert was automatically generated by the Render Service Keep-Alive & Monitoring system.
                </p>
            </body>
            </html>
        """
        
        return email_body
    
    def _save_alert_backup(self, alert_report):
        """Save alert to local backup file."""
        try:
            # Create backup directory
            backup_dir = "logs/alert_backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            alert_type = alert_report.get("alert_type", "UNKNOWN").lower()
            backup_file = os.path.join(backup_dir, f"alert_{alert_type}_{timestamp}.json")
            
            # Save alert as JSON
            with open(backup_file, "w") as f:
                json.dump(alert_report, f, indent=2)
            
            logger.info(f"Alert backup saved to {backup_file}")
            
            # Also save as HTML
            html_file = backup_file.replace(".json", ".html")
            with open(html_file, "w", encoding='utf-8') as f:
                f.write(self.format_alert_email(alert_report))
                
        except Exception as e:
            logger.error(f"Failed to save alert backup: {str(e)}")
    def send_report(self, report, retry_count=3, retry_delay=300):
        """Send the report with retry logic and local backup."""
        # Always save report locally first
        self._save_report_backup(report)
        
        for attempt in range(retry_count):
            if self.send_report_email(report):
                logger.info("Report successfully sent via email")
                return True
            
            if attempt < retry_count - 1:
                logger.warning(f"Email failed, retrying in {retry_delay} seconds (attempt {attempt + 1}/{retry_count})")
                import time
                time.sleep(retry_delay)
        
        logger.error(f"Failed to send report via email after {retry_count} attempts. Report saved locally.")
        return False
    
    def _save_report_backup(self, report):
        """Save report to local backup file."""
        try:
            # Create backup directory
            backup_dir = "logs/report_backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_file = os.path.join(backup_dir, f"report_backup_{timestamp}.json")
            
            # Save report as JSON
            with open(backup_file, "w") as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Report backup saved to {backup_file}")
            
            # Also save as HTML for easy viewing
            html_file = backup_file.replace(".json", ".html")
            with open(html_file, "w", encoding='utf-8') as f:
                f.write(self.format_report_email(report))
            
            logger.info(f"HTML report backup saved to {html_file}")
            
        except Exception as e:
            logger.error(f"Failed to save report backup: {str(e)}")


if __name__ == "__main__":
    # Example usage
    sample_report = {
        "report_date": datetime.datetime.now().isoformat(),
        "total_checks": 1440,
        "uptime_count": 1430,
        "downtime_count": 10,
        "uptime_percentage": 99.31,
        "downtime_timestamps": [
            "2023-01-01T12:34:56",
            "2023-01-01T13:45:67"
        ]
    }
    
    reporter = ServiceReporter()
    reporter.send_report(sample_report)