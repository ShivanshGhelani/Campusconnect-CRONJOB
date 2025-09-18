#!/usr/bin/env python3
"""Quick test of Campus Connect service"""

from keep_alive import RenderKeepAlive
from monitoring import ServiceMonitor  
from reporting import ServiceReporter
import time

print('🔍 Testing Campus Connect service...')
keep_alive = RenderKeepAlive('https://campusconnect-v2.onrender.com', ['/ping', '/api/health'], ['GET', 'HEAD'], 10)
monitor = ServiceMonitor()

# Run a few test pings
for i in range(3):
    print(f'Ping cycle {i+1}/3...')
    results = keep_alive.ping_all_endpoints()
    for result in results:
        monitor.log_ping(result['endpoint'], result['method'], result['status'], 
                        result['response_time_ms'], result.get('error'), result.get('status_code'))
    time.sleep(1)

# Generate test report
report = monitor.generate_report()
if report:
    reporter = ServiceReporter()
    reporter._save_report_backup(report)
    print(f'✅ Generated report: {report["uptime_percentage"]:.1f}% uptime ({report["uptime_count"]}/{report["total_checks"]} checks)')
    print(f'   Average response time: {report.get("average_response_time_ms", "N/A")}ms')
else:
    print('❌ No report generated')

print('\n🎉 Test completed! Check logs/report_backups/ for the generated report.')