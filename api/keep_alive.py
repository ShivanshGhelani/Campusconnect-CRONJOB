#!/usr/bin/env python3
"""
Keep-Alive module for Render Service Keep-Alive & Monitoring

This module handles the core keep-alive functionality by sending periodic
requests to prevent the Render service from going idle.

Author: Shivansh Ghelani
Version: 1.0
"""

import time
import requests
import datetime
from loguru import logger

# Configure logger
logger.add(
    "logs/keep_alive.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

class RenderKeepAlive:
    """Class for keeping Render service alive by periodic pinging."""
    
    def __init__(self, base_url, endpoints=None, methods=None, timeout=10):
        """Initialize the keep-alive service."""
        self.base_url = base_url.rstrip('/') if base_url else ""
        self.endpoints = endpoints or ["/ping", "/api/health"]
        self.methods = methods or ["GET", "HEAD"]
        self.timeout = timeout
        
        logger.info(f"Initialized RenderKeepAlive for {self.base_url}")
        logger.info(f"Endpoints: {self.endpoints}")
        logger.info(f"Methods: {self.methods}")
        logger.info(f"Timeout: {self.timeout} seconds")
    
    def ping_endpoint(self, endpoint, method="GET"):
        """
        Ping a single endpoint with the specified method.
        
        Returns:
            dict: Result containing status, response_time_ms, and error info
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "url": url,
            "status": "DOWN",
            "response_time_ms": None,
            "status_code": None,
            "error": None,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        try:
            logger.debug(f"Pinging {url} with {method}")
            
            # Make the request
            if method.upper() == "GET":
                response = requests.get(url, timeout=self.timeout)
            elif method.upper() == "HEAD":
                response = requests.head(url, timeout=self.timeout)
            else:
                logger.warning(f"Unsupported HTTP method: {method}. Using GET.")
                response = requests.get(url, timeout=self.timeout)
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            result["response_time_ms"] = response_time_ms
            result["status_code"] = response.status_code
            
            # Determine if the service is up based on status code
            if response.status_code < 400:
                result["status"] = "UP"
                logger.info(f"✓ {url} is UP (HTTP {response.status_code}) - {response_time_ms}ms")
            else:
                result["error"] = f"HTTP {response.status_code}"
                logger.warning(f"✗ {url} returned error status (HTTP {response.status_code}) - {response_time_ms}ms")
        
        except requests.exceptions.Timeout:
            result["error"] = f"Request timeout after {self.timeout}s"
            result["response_time_ms"] = self.timeout * 1000
            logger.error(f"✗ {url} timed out after {self.timeout} seconds")
        
        except requests.exceptions.ConnectionError as e:
            result["error"] = f"Connection error: {str(e)}"
            logger.error(f"✗ {url} connection failed: {str(e)}")
        
        except requests.exceptions.RequestException as e:
            result["error"] = f"Request error: {str(e)}"
            logger.error(f"✗ {url} request failed: {str(e)}")
        
        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
            logger.error(f"✗ {url} unexpected error: {str(e)}")
        
        return result
    
    def ping_all_endpoints(self):
        """
        Ping all configured endpoints with all configured methods.
        
        Returns:
            list: List of results for each endpoint/method combination
        """
        results = []
        
        for endpoint in self.endpoints:
            for method in self.methods:
                result = self.ping_endpoint(endpoint, method)
                results.append(result)
        
        return results
    
    def is_service_healthy(self, results):
        """
        Determine if the service is considered healthy based on ping results.
        
        Args:
            results (list): List of ping results
            
        Returns:
            bool: True if at least one endpoint is UP
        """
        return any(result["status"] == "UP" for result in results)


if __name__ == "__main__":
    # Example usage
    keep_alive = RenderKeepAlive(
        base_url="https://example-service.onrender.com",
        endpoints=["/ping", "/api/health"],
        methods=["GET", "HEAD"],
        timeout=10
    )
    
    results = keep_alive.ping_all_endpoints()
    for result in results:
        print(f"{result['method']} {result['endpoint']}: {result['status']} "
              f"({result.get('response_time_ms', 'N/A')}ms)")
    
    print(f"Service healthy: {keep_alive.is_service_healthy(results)}")