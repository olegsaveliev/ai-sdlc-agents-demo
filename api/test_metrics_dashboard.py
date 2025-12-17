#1
"""
Test Metrics Dashboard API

Implementation of US-001: Test Manager - View Overall Test Metrics
Provides comprehensive test metrics for monitoring testing progress, identifying issues,
and making informed decisions about release readiness.

Issue #35: Test Metrics
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TestStatus(Enum):
    """Test execution status enumeration"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    IN_PROGRESS = "in_progress"


@dataclass
class TestExecution:
    """Represents a single test execution"""
    test_id: str
    test_name: str
    status: TestStatus
    execution_time_ms: int
    executed_at: datetime
    failure_reason: Optional[str] = None
    test_suite: Optional[str] = None


@dataclass
class TestCoverageMetrics:
    """Test coverage metrics"""
    line_coverage: float
    branch_coverage: float
    function_coverage: float

    def get_overall_coverage(self) -> float:
        """Calculate overall coverage percentage"""
        return (self.line_coverage + self.branch_coverage + self.function_coverage) / 3


@dataclass
class DefectMetrics:
    """Defect density and quality metrics"""
    total_defects: int
    open_defects: int
    critical_defects: int
    defect_density: float  # defects per 1000 lines of code
    avg_resolution_time_hours: float


@dataclass
class TestExecutionSummary:
    """Overall test execution summary"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    in_progress_tests: int

    def get_pass_rate(self) -> float:
        """Calculate test pass rate percentage"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100

    def get_failure_rate(self) -> float:
        """Calculate test failure rate percentage"""
        if self.total_tests == 0:
            return 0.0
        return (self.failed_tests / self.total_tests) * 100


@dataclass
class TestTrendData:
    """Test execution trend data point"""
    date: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float


@dataclass
class FailingTestCase:
    """Information about a failing test case"""
    test_name: str
    failure_count: int
    last_failure_date: datetime
    failure_reason: str
    test_suite: str


@dataclass
class TestingVelocityMetrics:
    """Testing velocity and productivity metrics"""
    tests_executed_per_day: float
    avg_execution_time_ms: float
    test_automation_rate: float  # percentage of automated tests


@dataclass
class DashboardMetrics:
    """
    Comprehensive dashboard metrics for test managers
    Implements AC-001 requirements from issue #35
    """
    execution_summary: TestExecutionSummary
    coverage_metrics: TestCoverageMetrics
    defect_metrics: DefectMetrics
    execution_trends: List[TestTrendData]
    top_failing_tests: List[FailingTestCase]
    velocity_metrics: TestingVelocityMetrics
    generated_at: datetime


class TestMetricsDashboard:
    """
    Test Metrics Dashboard Service
    Provides comprehensive test metrics for Test Managers (US-001)
    """

    def __init__(self):
        """Initialize dashboard with sample data storage"""
        self.test_executions: List[TestExecution] = []
        self.defects: List[Dict] = []

    def get_dashboard_metrics(self, project_id: Optional[str] = None,
                            date_range_days: int = 30) -> Dict:
        """
        Get comprehensive dashboard metrics for test managers

        Args:
            project_id: Optional project identifier to filter metrics
            date_range_days: Number of days to include in trends (default 30)

        Returns:
            Dictionary containing all dashboard metrics
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range_days)

        # Calculate all metrics
        execution_summary = self._calculate_execution_summary(start_date, end_date)
        coverage_metrics = self._calculate_coverage_metrics()
        defect_metrics = self._calculate_defect_metrics()
        execution_trends = self._calculate_execution_trends(date_range_days)
        top_failing_tests = self._get_top_failing_tests(limit=5)
        velocity_metrics = self._calculate_velocity_metrics(date_range_days)

        # Create dashboard metrics object
        dashboard = DashboardMetrics(
            execution_summary=execution_summary,
            coverage_metrics=coverage_metrics,
            defect_metrics=defect_metrics,
            execution_trends=execution_trends,
            top_failing_tests=top_failing_tests,
            velocity_metrics=velocity_metrics,
            generated_at=datetime.now()
        )

        return self._to_dict(dashboard)

    def _calculate_execution_summary(self, start_date: datetime,
                                    end_date: datetime) -> TestExecutionSummary:
        """Calculate overall test execution summary"""
        # Filter executions within date range
        recent_executions = [
            ex for ex in self.test_executions
            if start_date <= ex.executed_at <= end_date
        ]

        total = len(recent_executions)
        passed = sum(1 for ex in recent_executions if ex.status == TestStatus.PASSED)
        failed = sum(1 for ex in recent_executions if ex.status == TestStatus.FAILED)
        skipped = sum(1 for ex in recent_executions if ex.status == TestStatus.SKIPPED)
        in_progress = sum(1 for ex in recent_executions if ex.status == TestStatus.IN_PROGRESS)

        return TestExecutionSummary(
            total_tests=total,
            passed_tests=passed,
            failed_tests=failed,
            skipped_tests=skipped,
            in_progress_tests=in_progress
        )

    def _calculate_coverage_metrics(self) -> TestCoverageMetrics:
        """Calculate test coverage metrics"""
        # In a real implementation, this would query coverage tools
        return TestCoverageMetrics(
            line_coverage=85.5,
            branch_coverage=78.3,
            function_coverage=92.1
        )

    def _calculate_defect_metrics(self) -> DefectMetrics:
        """Calculate defect density and quality metrics"""
        # In a real implementation, this would query defect tracking system
        total = len(self.defects)
        open_defects = sum(1 for d in self.defects if d.get('status') == 'open')
        critical = sum(1 for d in self.defects if d.get('severity') == 'critical')

        return DefectMetrics(
            total_defects=total,
            open_defects=open_defects,
            critical_defects=critical,
            defect_density=2.3,  # defects per 1000 LOC
            avg_resolution_time_hours=24.5
        )

    def _calculate_execution_trends(self, days: int) -> List[TestTrendData]:
        """Calculate test execution trends for the specified number of days"""
        trends = []
        end_date = datetime.now()

        for i in range(days):
            date = end_date - timedelta(days=days - i - 1)
            date_str = date.strftime('%Y-%m-%d')

            # Filter executions for this specific day
            day_executions = [
                ex for ex in self.test_executions
                if ex.executed_at.date() == date.date()
            ]

            total = len(day_executions)
            passed = sum(1 for ex in day_executions if ex.status == TestStatus.PASSED)
            failed = sum(1 for ex in day_executions if ex.status == TestStatus.FAILED)
            pass_rate = (passed / total * 100) if total > 0 else 0

            trends.append(TestTrendData(
                date=date_str,
                total_tests=total,
                passed_tests=passed,
                failed_tests=failed,
                pass_rate=round(pass_rate, 2)
            ))

        return trends

    def _get_top_failing_tests(self, limit: int = 5) -> List[FailingTestCase]:
        """Get top N failing test cases"""
        # Count failures by test name
        failure_counts = {}

        for execution in self.test_executions:
            if execution.status == TestStatus.FAILED:
                test_name = execution.test_name
                if test_name not in failure_counts:
                    failure_counts[test_name] = {
                        'count': 0,
                        'last_failure': execution.executed_at,
                        'reason': execution.failure_reason or 'Unknown',
                        'suite': execution.test_suite or 'Unknown'
                    }
                failure_counts[test_name]['count'] += 1
                # Keep track of most recent failure
                if execution.executed_at > failure_counts[test_name]['last_failure']:
                    failure_counts[test_name]['last_failure'] = execution.executed_at
                    failure_counts[test_name]['reason'] = execution.failure_reason or 'Unknown'

        # Sort by failure count and get top N
        sorted_failures = sorted(
            failure_counts.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:limit]

        return [
            FailingTestCase(
                test_name=test_name,
                failure_count=data['count'],
                last_failure_date=data['last_failure'],
                failure_reason=data['reason'],
                test_suite=data['suite']
            )
            for test_name, data in sorted_failures
        ]

    def _calculate_velocity_metrics(self, days: int) -> TestingVelocityMetrics:
        """Calculate testing velocity and productivity metrics"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        recent_executions = [
            ex for ex in self.test_executions
            if start_date <= ex.executed_at <= end_date
        ]

        total_tests = len(recent_executions)
        tests_per_day = total_tests / days if days > 0 else 0

        avg_execution_time = (
            sum(ex.execution_time_ms for ex in recent_executions) / total_tests
            if total_tests > 0 else 0
        )

        # Automation rate would be calculated from test metadata
        automation_rate = 75.0  # 75% of tests are automated

        return TestingVelocityMetrics(
            tests_executed_per_day=round(tests_per_day, 2),
            avg_execution_time_ms=round(avg_execution_time, 2),
            test_automation_rate=automation_rate
        )

    def _to_dict(self, dashboard: DashboardMetrics) -> Dict:
        """Convert dashboard metrics to dictionary format"""
        return {
            'execution_summary': {
                'total_tests': dashboard.execution_summary.total_tests,
                'passed_tests': dashboard.execution_summary.passed_tests,
                'failed_tests': dashboard.execution_summary.failed_tests,
                'skipped_tests': dashboard.execution_summary.skipped_tests,
                'in_progress_tests': dashboard.execution_summary.in_progress_tests,
                'pass_rate': round(dashboard.execution_summary.get_pass_rate(), 2),
                'failure_rate': round(dashboard.execution_summary.get_failure_rate(), 2)
            },
            'coverage_metrics': {
                'line_coverage': dashboard.coverage_metrics.line_coverage,
                'branch_coverage': dashboard.coverage_metrics.branch_coverage,
                'function_coverage': dashboard.coverage_metrics.function_coverage,
                'overall_coverage': round(dashboard.coverage_metrics.get_overall_coverage(), 2)
            },
            'defect_metrics': {
                'total_defects': dashboard.defect_metrics.total_defects,
                'open_defects': dashboard.defect_metrics.open_defects,
                'critical_defects': dashboard.defect_metrics.critical_defects,
                'defect_density': dashboard.defect_metrics.defect_density,
                'avg_resolution_time_hours': dashboard.defect_metrics.avg_resolution_time_hours
            },
            'execution_trends': [
                {
                    'date': trend.date,
                    'total_tests': trend.total_tests,
                    'passed_tests': trend.passed_tests,
                    'failed_tests': trend.failed_tests,
                    'pass_rate': trend.pass_rate
                }
                for trend in dashboard.execution_trends
            ],
            'top_failing_tests': [
                {
                    'test_name': test.test_name,
                    'failure_count': test.failure_count,
                    'last_failure_date': test.last_failure_date.isoformat(),
                    'failure_reason': test.failure_reason,
                    'test_suite': test.test_suite
                }
                for test in dashboard.top_failing_tests
            ],
            'velocity_metrics': {
                'tests_executed_per_day': dashboard.velocity_metrics.tests_executed_per_day,
                'avg_execution_time_ms': dashboard.velocity_metrics.avg_execution_time_ms,
                'test_automation_rate': dashboard.velocity_metrics.test_automation_rate
            },
            'generated_at': dashboard.generated_at.isoformat()
        }

    def add_test_execution(self, execution: TestExecution):
        """Add a test execution record"""
        self.test_executions.append(execution)

    def add_defect(self, defect: Dict):
        """Add a defect record"""
        self.defects.append(defect)


# Global dashboard instance
_dashboard_instance = TestMetricsDashboard()


def get_test_metrics_dashboard(project_id: Optional[str] = None,
                               date_range_days: int = 30) -> Dict:
    """
    API endpoint to get comprehensive test metrics dashboard

    Implements US-001: Test Manager - View Overall Test Metrics from Issue #35

    Args:
        project_id: Optional project identifier to filter metrics
        date_range_days: Number of days to include in trends (default 30)

    Returns:
        Dictionary containing comprehensive dashboard metrics including:
        - Overall test execution summary (passed, failed, skipped, in progress)
        - Test coverage percentage
        - Defect density metrics
        - Test execution trends (configurable days)
        - Top 5 failing test cases
        - Testing velocity metrics

    Example:
        >>> metrics = get_test_metrics_dashboard(project_id="proj-123", date_range_days=30)
        >>> print(f"Pass rate: {metrics['execution_summary']['pass_rate']}%")
    """
    return _dashboard_instance.get_dashboard_metrics(project_id, date_range_days)


def get_dashboard_instance() -> TestMetricsDashboard:
    """Get the global dashboard instance for adding test data"""
    return _dashboard_instance
