#1.5
"""
Performance Metrics Tracking System

This module provides functionality to collect and track performance metrics
for the application, including response times, request counts, and error rates.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional


class MetricsCollector:
    """
    Collects and stores performance metrics for the application.
    """

    def __init__(self):
        """Initialize the metrics collector with empty storage."""
        self.metrics = {
            'request_count': 0,
            'error_count': 0,
            'response_times': [],
            'requests_by_endpoint': {},
            'errors_by_type': {},
        }
        self.start_time = datetime.now()

    def record_request(self, endpoint: str, response_time: float, status_code: int):
        """
        Record a request with its response time and status code.

        Args:
            endpoint: The API endpoint that was called
            response_time: The time taken to process the request in seconds
            status_code: The HTTP status code returned
        """
        self.metrics['request_count'] += 1
        self.metrics['response_times'].append(response_time)

        # Track requests by endpoint
        if endpoint not in self.metrics['requests_by_endpoint']:
            self.metrics['requests_by_endpoint'][endpoint] = {
                'count': 0,
                'total_time': 0,
                'avg_time': 0
            }

        endpoint_stats = self.metrics['requests_by_endpoint'][endpoint]
        endpoint_stats['count'] += 1
        endpoint_stats['total_time'] += response_time
        endpoint_stats['avg_time'] = endpoint_stats['total_time'] / endpoint_stats['count']

        # Track errors
        if status_code >= 400:
            self.record_error(f"HTTP_{status_code}")

    def record_error(self, error_type: str):
        """
        Record an error by type.

        Args:
            error_type: The type or category of error
        """
        self.metrics['error_count'] += 1

        if error_type not in self.metrics['errors_by_type']:
            self.metrics['errors_by_type'][error_type] = 0

        self.metrics['errors_by_type'][error_type] += 1

    def get_average_response_time(self) -> float:
        """
        Calculate and return the average response time.

        Returns:
            The average response time in seconds, or 0 if no requests recorded
        """
        if not self.metrics['response_times']:
            return 0.0
        return sum(self.metrics['response_times']) / len(self.metrics['response_times'])

    def get_error_rate(self) -> float:
        """
        Calculate and return the error rate as a percentage.

        Returns:
            The error rate as a percentage (0-100)
        """
        if self.metrics['request_count'] == 0:
            return 0.0
        return (self.metrics['error_count'] / self.metrics['request_count']) * 100

    def get_summary(self) -> Dict:
        """
        Get a summary of all collected metrics.

        Returns:
            A dictionary containing all metrics and statistics
        """
        uptime = (datetime.now() - self.start_time).total_seconds()

        return {
            'total_requests': self.metrics['request_count'],
            'total_errors': self.metrics['error_count'],
            'error_rate': round(self.get_error_rate(), 2),
            'average_response_time': round(self.get_average_response_time(), 4),
            'uptime_seconds': round(uptime, 2),
            'requests_by_endpoint': self.metrics['requests_by_endpoint'],
            'errors_by_type': self.metrics['errors_by_type'],
        }

    def reset_metrics(self):
        """Reset all metrics to their initial state."""
        self.__init__()


# Global metrics collector instance
_global_metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """
    Get the global metrics collector instance.

    Returns:
        The global MetricsCollector instance
    """
    return _global_metrics_collector


def track_performance(func):
    """
    Decorator to automatically track performance metrics for a function.

    Usage:
        @track_performance
        def my_api_endpoint():
            # Your code here
            pass
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        error_occurred = False

        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error_occurred = True
            get_metrics_collector().record_error(type(e).__name__)
            raise
        finally:
            elapsed_time = time.time() - start_time
            status_code = 500 if error_occurred else 200
            get_metrics_collector().record_request(
                func.__name__,
                elapsed_time,
                status_code
            )

    return wrapper
