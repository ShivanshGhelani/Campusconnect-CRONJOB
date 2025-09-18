#!/usr/bin/env python3
"""
Test script for Render Service Keep-Alive & Monitoring

This script validates the functionality of all components before deployment.

Author: Shivansh Ghelani  
Version: 1.0
"""

import os
import json
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all modules can be imported successfully."""
    print("🔍 Testing imports...")
    try:
        from keep_alive import RenderKeepAlive
        from monitoring import ServiceMonitor
        from reporting import ServiceReporter
        from main import RenderServiceManager
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("⚙️ Testing configuration...")
    
    # Test config.json
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
            print("✅ config.json loaded successfully")
        except json.JSONDecodeError as e:
            print(f"❌ config.json has invalid JSON: {e}")
            return False
    else:
        print("❌ config.json not found")
        return False
    
    # Test .env file
    if os.path.exists(".env"):
        base_url = os.getenv("BASE_URL")
        email_user = os.getenv("EMAIL_USER")
        if base_url and email_user:
            print("✅ .env file configured with required variables")
        else:
            print("⚠️ .env file missing some required variables (BASE_URL, EMAIL_USER)")
    else:
        print("⚠️ .env file not found - using defaults")
    
    return True

def test_keep_alive():
    """Test keep-alive functionality."""
    print("🚀 Testing keep-alive module...")
    
    try:
        from keep_alive import RenderKeepAlive
        
        # Test with example URL (this will fail but should handle gracefully)
        keep_alive = RenderKeepAlive(
            base_url="https://httpbin.org",
            endpoints=["/status/200", "/status/404"],
            methods=["GET", "HEAD"],
            timeout=5
        )
        
        print("✅ RenderKeepAlive initialized successfully")
        
        # Test a ping (this should work with httpbin.org)
        results = keep_alive.ping_all_endpoints()
        print(f"✅ Ping test completed - {len(results)} results returned")
        
        # Check if results have expected structure
        for result in results:
            required_keys = ["endpoint", "method", "status", "timestamp"]
            if all(key in result for key in required_keys):
                print(f"✅ Result structure valid for {result['method']} {result['endpoint']}")
            else:
                print(f"❌ Invalid result structure: {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Keep-alive test failed: {e}")
        return False

def test_monitoring():
    """Test monitoring functionality."""
    print("📊 Testing monitoring module...")
    
    try:
        from monitoring import ServiceMonitor
        
        monitor = ServiceMonitor("logs/test_uptime_logs.json")
        
        # Test logging
        monitor.log_ping("/test", "GET", "UP", 150, None, 200)
        monitor.log_ping("/test", "GET", "DOWN", None, "Connection error", None)
        
        print("✅ Monitoring logging works")
        
        # Test report generation
        report = monitor.generate_report()
        if report and "total_checks" in report:
            print("✅ Report generation works")
            print(f"   Report contains {report['total_checks']} checks")
        else:
            print("❌ Report generation failed")
            return False
        
        # Clean up test file
        if os.path.exists("logs/test_uptime_logs.json"):
            os.remove("logs/test_uptime_logs.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Monitoring test failed: {e}")
        return False

def test_reporting():
    """Test reporting functionality."""
    print("📧 Testing reporting module...")
    
    try:
        from reporting import ServiceReporter
        
        reporter = ServiceReporter()
        
        # Create sample report
        sample_report = {
            "report_date": datetime.datetime.now().isoformat(),
            "total_checks": 100,
            "uptime_count": 95,
            "downtime_count": 5,
            "uptime_percentage": 95.0,
            "average_response_time_ms": 250.5,
            "downtime_incidents": [
                {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "endpoint": "/api/health",
                    "method": "GET",
                    "error": "Connection timeout"
                }
            ]
        }
        
        # Test HTML formatting
        html_content = reporter.format_report_email(sample_report)
        if html_content and "<html>" in html_content:
            print("✅ HTML report formatting works")
        else:
            print("❌ HTML report formatting failed")
            return False
        
        # Test backup functionality (without sending email)
        reporter._save_report_backup(sample_report)
        backup_dir = "logs/report_backups"
        if os.path.exists(backup_dir) and os.listdir(backup_dir):
            print("✅ Report backup functionality works")
        else:
            print("❌ Report backup functionality failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Reporting test failed: {e}")
        return False

def test_directory_structure():
    """Test that all necessary directories exist."""
    print("📁 Testing directory structure...")
    
    required_dirs = ["logs", "logs/report_backups"]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory {dir_path} exists")
        else:
            print(f"⚠️ Creating missing directory {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
    
    return True

def main():
    """Run all tests."""
    print("🧪 Render Service Keep-Alive & Monitoring - Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_configuration,
        test_directory_structure,
        test_keep_alive,
        test_monitoring,
        test_reporting
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your service is ready to deploy.")
        print("\nNext steps:")
        print("1. Update your .env file with real service URL and email credentials")
        print("2. Test with your actual service: python main.py --report-now")
        print("3. Start the service: run_service.bat")
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()