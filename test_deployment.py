#!/usr/bin/env python3
"""
Test script for Campus Connect monitoring system.
Tests both local Windows service and Vercel deployment functionality.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

def test_imports():
    """Test all required imports work correctly."""
    print("🧪 Testing imports...")
    
    try:
        # Core modules
        from keep_alive import RenderKeepAlive
        from monitoring import ServiceMonitor  
        from reporting import ServiceReporter
        from main import RenderServiceManager
        print("✅ Core modules imported successfully")
        
        # FastAPI modules for Vercel
        try:
            from fastapi import FastAPI
            from pydantic import BaseModel
            print("✅ FastAPI modules available")
        except ImportError:
            print("⚠️ FastAPI not installed (install with: pip install fastapi uvicorn)")
            
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\n🔧 Testing configuration...")
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print(f"✅ Configuration loaded")
        print(f"   Service: {config.get('service_name')}")
        print(f"   URL: {config.get('base_url')}")
        print(f"   Endpoints: {config.get('endpoints')}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_service_connectivity():
    """Test connection to Campus Connect service."""
    print("\n🌐 Testing Campus Connect connectivity...")
    
    try:
        from keep_alive import RenderKeepAlive
        
        # Initialize keep-alive with Campus Connect URL
        keep_alive = RenderKeepAlive(
            base_url="https://campusconnect-v2.onrender.com",
            endpoints=["/ping", "/api/health"],
            timeout=10
        )
        
        # Test ping
        result = keep_alive.ping_all_endpoints()
        if result:
            print("✅ Campus Connect is responding")
            successful_pings = [r for r in result if r.get('success', False)]
            print(f"   Successful pings: {len(successful_pings)}/{len(result)}")
            
            for ping in result:
                status = "✅" if ping.get('success', False) else "❌"
                response_time = ping.get('response_time', 'N/A')
                print(f"   {status} {ping['method']} {ping['endpoint']}: {response_time}ms")
                
            return True
        else:
            print("❌ No successful pings to Campus Connect")
            return False
            
    except Exception as e:
        print(f"❌ Connectivity test failed: {e}")
        return False

def test_email_configuration():
    """Test email configuration (without sending)."""
    print("\n📧 Testing email configuration...")
    
    try:
        from reporting import ServiceReporter
        
        # Check for environment variables
        required_vars = ['SMTP_USERNAME', 'SMTP_PASSWORD', 'SENDER_EMAIL', 'RECIPIENT_EMAIL']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var) and not os.getenv(var.replace('SMTP_', 'EMAIL_').replace('SENDER_', 'FROM_')):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️ Missing environment variables: {missing_vars}")
            print("   Set up .env file for email functionality")
        else:
            print("✅ Email configuration variables found")
            
        # Test reporter initialization
        reporter = ServiceReporter("Campus Connect Backend")
        print("✅ ServiceReporter initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Email configuration test failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI application for Vercel deployment."""
    print("\n🚀 Testing FastAPI application...")
    
    try:
        # Change to api directory to import
        sys.path.insert(0, str(Path(__file__).parent / "api"))
        
        from index import app, MonitoringService
        
        print("✅ FastAPI app imported successfully")
        
        # Test monitoring service initialization
        monitoring = MonitoringService()
        print("✅ MonitoringService initialized")
        
        print(f"   App title: {app.title}")
        print(f"   App version: {app.version}")
        
        # List available routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        print(f"   Available routes: {routes}")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI test failed: {e}")
        return False

def test_logs_directory():
    """Test logs directory structure."""
    print("\n📁 Testing logs directory...")
    
    logs_dir = Path("logs")
    
    if not logs_dir.exists():
        logs_dir.mkdir(exist_ok=True)
        print("✅ Created logs directory")
    else:
        print("✅ Logs directory exists")
        
    # Check for existing log files
    log_files = list(logs_dir.glob("*.log")) + list(logs_dir.glob("*.json"))
    
    if log_files:
        print(f"   Found {len(log_files)} existing log files")
        for log_file in log_files[:5]:  # Show first 5
            print(f"   - {log_file.name}")
        if len(log_files) > 5:
            print(f"   ... and {len(log_files) - 5} more")
    else:
        print("   No existing log files (will be created during monitoring)")
        
    return True

def run_tests():
    """Run all test functions."""
    print("🏁 Campus Connect Monitoring System - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration), 
        ("Service Connectivity", test_service_connectivity),
        ("Email Configuration", test_email_configuration),
        ("FastAPI Application", test_fastapi_app),
        ("Logs Directory", test_logs_directory)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("-" * 30)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System ready for deployment.")
        
        print("\n🚀 Next Steps:")
        print("  For Vercel deployment: See VERCEL_DEPLOY.md")
        print("  For local service: Run run_service.bat")
        print("  To test monitoring: python main.py")
        
    else:
        print("⚠️ Some tests failed. Please address issues before deployment.")
        
    return passed == total

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)