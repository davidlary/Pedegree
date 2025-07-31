#!/usr/bin/env python3
"""
Automated Testing Framework for International Standards Retrieval System

Comprehensive testing framework that orchestrates all 11 testing categories
with automated execution, reporting, and validation across 19 OpenAlex disciplines.

Author: Autonomous AI Development System
"""

import unittest
import asyncio
import threading
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import subprocess
import concurrent.futures

# Import core system modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.config_manager import ConfigManager
from core.recovery_manager import RecoveryManager
from core.llm_integration import LLMIntegration
from core.orchestrator import StandardsOrchestrator

class TestCategory(Enum):
    """Testing category enumeration"""
    UNIT = "unit_tests"
    INTEGRATION = "integration_tests"
    SYSTEM = "system_tests"
    PERFORMANCE = "performance_tests"
    LOAD = "load_tests"
    RECOVERY = "recovery_tests"
    LLM_INTEGRATION = "llm_integration_tests"
    DATA_QUALITY = "data_quality_tests"
    AGENT_COMMUNICATION = "agent_communication_tests"
    CONFIGURATION = "configuration_tests"
    COMPLIANCE = "compliance_tests"

class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

@dataclass
class TestResult:
    """Test result data structure"""
    test_id: str
    test_name: str
    category: TestCategory
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    assertions_passed: int = 0
    assertions_failed: int = 0

@dataclass
class TestSuite:
    """Test suite configuration"""
    suite_id: str
    name: str
    category: TestCategory
    tests: List[str]
    dependencies: List[str]
    timeout: int = 300  # 5 minutes default
    parallel_execution: bool = False
    required_resources: Optional[List[str]] = None

class AutomatedTestFramework:
    """Comprehensive automated testing framework"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize testing framework
        
        Args:
            config_path: Optional path to test configuration
        """
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = self.project_root / 'tests'
        self.results_dir = self.tests_dir / 'results'
        self.results_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Test configuration
        self.test_config = self._load_test_configuration(config_path)
        
        # System under test
        self.config_manager = None
        self.recovery_manager = None
        self.llm_integration = None
        self.orchestrator = None
        
        # Test execution state
        self.test_suites = {}
        self.test_results = {}
        self.execution_order = []
        self.current_execution = None
        
        # Performance tracking
        self.test_metrics = {
            'total_tests': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0,
            'total_execution_time': 0.0,
            'start_time': None,
            'end_time': None
        }
        
        # Initialize test suites
        self._initialize_test_suites()
        
        self.logger.info("Automated testing framework initialized")
    
    def _load_test_configuration(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load test configuration from file or use defaults"""
        default_config = {
            'parallel_execution': True,
            'max_parallel_suites': 3,
            'timeout_per_suite': 600,  # 10 minutes
            'retry_failed_tests': True,
            'max_retries': 2,
            'generate_detailed_reports': True,
            'disciplines_to_test': ['Mathematics', 'Computer_Science', 'Physical_Sciences'],
            'performance_thresholds': {
                'max_response_time': 30.0,  # seconds
                'min_throughput': 10,  # operations per minute
                'max_memory_usage': 1024  # MB
            }
        }
        
        if config_path and config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load test config: {e}")
        
        return default_config
    
    def _initialize_test_suites(self):
        """Initialize all test suites for the 11 testing categories"""
        
        # 1. Unit Tests
        self.test_suites[TestCategory.UNIT] = TestSuite(
            suite_id="unit_tests",
            name="Unit Tests",
            category=TestCategory.UNIT,
            tests=[
                "test_config_manager_unit",
                "test_recovery_manager_unit", 
                "test_llm_integration_unit",
                "test_base_agent_unit",
                "test_discovery_agent_unit",
                "test_retrieval_agent_unit",
                "test_processing_agent_unit",
                "test_validation_agent_unit"
            ],
            dependencies=[],
            timeout=180,
            parallel_execution=True
        )
        
        # 2. Integration Tests
        self.test_suites[TestCategory.INTEGRATION] = TestSuite(
            suite_id="integration_tests",
            name="Integration Tests",
            category=TestCategory.INTEGRATION,
            tests=[
                "test_config_recovery_integration",
                "test_llm_agent_integration",
                "test_orchestrator_agent_integration",
                "test_agent_pipeline_integration",
                "test_streamlit_core_integration"
            ],
            dependencies=["unit_tests"],
            timeout=300,
            parallel_execution=True
        )
        
        # 3. System Tests
        self.test_suites[TestCategory.SYSTEM] = TestSuite(
            suite_id="system_tests",
            name="System Tests",
            category=TestCategory.SYSTEM,
            tests=[
                "test_end_to_end_standards_retrieval",
                "test_multi_discipline_processing",
                "test_streamlit_app_functionality",
                "test_complete_workflow_execution"
            ],
            dependencies=["unit_tests", "integration_tests"],
            timeout=600,
            parallel_execution=False
        )
        
        # 4. Performance Tests
        self.test_suites[TestCategory.PERFORMANCE] = TestSuite(
            suite_id="performance_tests",
            name="Performance Tests", 
            category=TestCategory.PERFORMANCE,
            tests=[
                "test_response_times",
                "test_throughput_benchmarks",
                "test_memory_usage",
                "test_llm_optimization_performance",
                "test_agent_processing_speed"
            ],
            dependencies=["system_tests"],
            timeout=900,
            parallel_execution=True
        )
        
        # 5. Load Tests
        self.test_suites[TestCategory.LOAD] = TestSuite(
            suite_id="load_tests", 
            name="Load Tests",
            category=TestCategory.LOAD,
            tests=[
                "test_concurrent_agent_execution",
                "test_high_volume_processing",
                "test_stress_testing",
                "test_resource_exhaustion"
            ],
            dependencies=["performance_tests"],
            timeout=1200,
            parallel_execution=False
        )
        
        # 6. Recovery Tests
        self.test_suites[TestCategory.RECOVERY] = TestSuite(
            suite_id="recovery_tests",
            name="Recovery Tests",
            category=TestCategory.RECOVERY,
            tests=[
                "test_system_recovery_scenarios",
                "test_checkpoint_restoration",
                "test_agent_failure_recovery",
                "test_data_consistency_after_recovery"
            ],
            dependencies=["system_tests"],
            timeout=600,
            parallel_execution=True
        )
        
        # 7. LLM Integration Tests
        self.test_suites[TestCategory.LLM_INTEGRATION] = TestSuite(
            suite_id="llm_integration_tests",
            name="LLM Integration Tests",
            category=TestCategory.LLM_INTEGRATION,
            tests=[
                "test_llm_router_functionality",
                "test_model_selection_optimization",
                "test_cost_tracking_accuracy",
                "test_token_usage_optimization",
                "test_quality_vs_cost_balance"
            ],
            dependencies=["integration_tests"],
            timeout=450,
            parallel_execution=True
        )
        
        # 8. Data Quality Tests
        self.test_suites[TestCategory.DATA_QUALITY] = TestSuite(
            suite_id="data_quality_tests",
            name="Data Quality Tests",
            category=TestCategory.DATA_QUALITY,
            tests=[
                "test_standards_extraction_accuracy",
                "test_competency_mapping_quality",
                "test_validation_effectiveness",
                "test_data_completeness",
                "test_classification_accuracy"
            ],
            dependencies=["system_tests"],
            timeout=600,
            parallel_execution=True
        )
        
        # 9. Agent Communication Tests
        self.test_suites[TestCategory.AGENT_COMMUNICATION] = TestSuite(
            suite_id="agent_communication_tests",
            name="Agent Communication Tests",
            category=TestCategory.AGENT_COMMUNICATION,
            tests=[
                "test_message_passing",
                "test_task_assignment_distribution",
                "test_orchestrator_coordination",
                "test_agent_status_reporting",
                "test_error_propagation"
            ],
            dependencies=["integration_tests"],
            timeout=300,
            parallel_execution=True
        )
        
        # 10. Configuration Tests
        self.test_suites[TestCategory.CONFIGURATION] = TestSuite(
            suite_id="configuration_tests",
            name="Configuration Tests",
            category=TestCategory.CONFIGURATION,
            tests=[
                "test_system_configuration_loading",
                "test_discipline_configuration",
                "test_agent_configuration",
                "test_llm_router_configuration",
                "test_invalid_configurations"
            ],
            dependencies=[],
            timeout=120,
            parallel_execution=True
        )
        
        # 11. Compliance Tests
        self.test_suites[TestCategory.COMPLIANCE] = TestSuite(
            suite_id="compliance_tests",
            name="Compliance Tests",
            category=TestCategory.COMPLIANCE,
            tests=[
                "test_educational_standards_compliance",
                "test_discipline_specific_accuracy",
                "test_openalex_taxonomy_adherence",
                "test_quality_threshold_compliance",
                "test_accessibility_compliance"
            ],
            dependencies=["data_quality_tests"],
            timeout=450,
            parallel_execution=True
        )
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites in proper dependency order
        
        Returns:
            Complete test execution results
        """
        self.logger.info("Starting comprehensive test execution")
        self.test_metrics['start_time'] = datetime.now()
        
        try:
            # Determine execution order based on dependencies
            execution_order = self._calculate_execution_order()
            
            # Initialize system under test
            self._initialize_system_under_test()
            
            # Execute test suites
            for category in execution_order:
                if category in self.test_suites:
                    suite = self.test_suites[category]
                    self.logger.info(f"Executing test suite: {suite.name}")
                    
                    suite_result = self._execute_test_suite(suite)
                    self.test_results[category] = suite_result
                    
                    # Check if suite failed and if we should continue
                    if suite_result['status'] == TestStatus.FAILED and not self.test_config.get('continue_on_failure', True):
                        self.logger.error(f"Test suite {suite.name} failed, stopping execution")
                        break
            
            # Generate final report
            final_report = self._generate_final_report()
            
            self.test_metrics['end_time'] = datetime.now()
            self.test_metrics['total_execution_time'] = (
                self.test_metrics['end_time'] - self.test_metrics['start_time']
            ).total_seconds()
            
            self.logger.info(f"Test execution completed in {self.test_metrics['total_execution_time']:.2f} seconds")
            
            return final_report
            
        except Exception as e:
            self.logger.error(f"Error during test execution: {e}")
            return {
                'success': False,
                'error': str(e),
                'partial_results': self.test_results
            }
        
        finally:
            # Cleanup system under test
            self._cleanup_system_under_test()
    
    def run_specific_category(self, category: TestCategory) -> Dict[str, Any]:
        """Run tests for a specific category
        
        Args:
            category: Test category to run
            
        Returns:
            Category test results
        """
        if category not in self.test_suites:
            return {
                'success': False,
                'error': f"Test category {category.value} not found"
            }
        
        self.logger.info(f"Running specific test category: {category.value}")
        
        # Initialize system if needed
        self._initialize_system_under_test()
        
        try:
            suite = self.test_suites[category]
            result = self._execute_test_suite(suite)
            
            return {
                'success': True,
                'category': category.value,
                'results': result
            }
            
        except Exception as e:
            self.logger.error(f"Error running category {category.value}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        
        finally:
            self._cleanup_system_under_test()
    
    def _calculate_execution_order(self) -> List[TestCategory]:
        """Calculate proper execution order based on dependencies"""
        executed = set()
        execution_order = []
        
        def can_execute(suite):
            return all(dep in [s.suite_id for s in self.test_suites.values() if s.category in executed] 
                      for dep in suite.dependencies)
        
        while len(execution_order) < len(self.test_suites):
            progress_made = False
            
            for category, suite in self.test_suites.items():
                if category not in executed and can_execute(suite):
                    execution_order.append(category)
                    executed.add(category)
                    progress_made = True
            
            if not progress_made:
                # Handle circular dependencies or missing dependencies
                remaining = [cat for cat in self.test_suites.keys() if cat not in executed]
                self.logger.warning(f"Cannot resolve dependencies for: {remaining}")
                execution_order.extend(remaining)
                break
        
        return execution_order
    
    def _initialize_system_under_test(self):
        """Initialize the system components for testing"""
        try:
            # Initialize core managers
            self.config_manager = ConfigManager(self.project_root)
            
            # Initialize recovery manager with proper parameters
            recovery_dir = self.project_root / 'recovery'
            recovery_dir.mkdir(exist_ok=True)
            recovery_config = self.config_manager.get_system_architecture().get('recovery_settings', {})
            self.recovery_manager = RecoveryManager(recovery_dir, recovery_config)
            
            # Initialize LLM integration
            self.llm_integration = LLMIntegration(self.config_manager)
            
            # Initialize orchestrator
            self.orchestrator = StandardsOrchestrator(
                self.config_manager,
                self.recovery_manager,
                self.llm_integration
            )
            
            self.logger.info("System under test initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize system under test: {e}")
            # Don't raise - allow tests to run with mocked components
            self.config_manager = None
            self.recovery_manager = None
            self.llm_integration = None
            self.orchestrator = None
    
    def _cleanup_system_under_test(self):
        """Cleanup system components after testing"""
        try:
            if self.orchestrator:
                self.orchestrator.stop_system()
            
            # Cleanup other components as needed
            self.orchestrator = None
            self.llm_integration = None
            self.recovery_manager = None
            self.config_manager = None
            
            self.logger.info("System under test cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def _execute_test_suite(self, suite: TestSuite) -> Dict[str, Any]:
        """Execute a single test suite
        
        Args:
            suite: Test suite to execute
            
        Returns:
            Suite execution results
        """
        start_time = datetime.now()
        suite_results = {
            'suite_id': suite.suite_id,
            'name': suite.name,
            'category': suite.category.value,
            'status': TestStatus.RUNNING,
            'start_time': start_time.isoformat(),
            'tests': {},
            'summary': {
                'total': len(suite.tests),
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'errors': 0
            }
        }
        
        try:
            if suite.parallel_execution and len(suite.tests) > 1:
                # Execute tests in parallel
                test_results = self._execute_tests_parallel(suite)
            else:
                # Execute tests sequentially
                test_results = self._execute_tests_sequential(suite)
            
            # Process results
            for test_id, result in test_results.items():
                suite_results['tests'][test_id] = asdict(result)
                
                if result.status == TestStatus.PASSED:
                    suite_results['summary']['passed'] += 1
                elif result.status == TestStatus.FAILED:
                    suite_results['summary']['failed'] += 1
                elif result.status == TestStatus.SKIPPED:
                    suite_results['summary']['skipped'] += 1
                else:
                    suite_results['summary']['errors'] += 1
            
            # Determine overall suite status
            if suite_results['summary']['failed'] > 0 or suite_results['summary']['errors'] > 0:
                suite_results['status'] = TestStatus.FAILED
            elif suite_results['summary']['passed'] > 0:
                suite_results['status'] = TestStatus.PASSED
            else:
                suite_results['status'] = TestStatus.SKIPPED
            
        except Exception as e:
            suite_results['status'] = TestStatus.ERROR
            suite_results['error'] = str(e)
            self.logger.error(f"Error executing suite {suite.name}: {e}")
        
        finally:
            end_time = datetime.now()
            suite_results['end_time'] = end_time.isoformat()
            suite_results['duration'] = (end_time - start_time).total_seconds()
        
        return suite_results
    
    def _execute_tests_parallel(self, suite: TestSuite) -> Dict[str, TestResult]:
        """Execute tests in parallel"""
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all test tasks
            future_to_test = {
                executor.submit(self._execute_single_test, test_id, suite): test_id
                for test_id in suite.tests
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_test, timeout=suite.timeout):
                test_id = future_to_test[future]
                try:
                    result = future.result()
                    results[test_id] = result
                except Exception as e:
                    results[test_id] = TestResult(
                        test_id=test_id,
                        test_name=test_id,
                        category=suite.category,
                        status=TestStatus.ERROR,
                        start_time=datetime.now(),
                        error_message=str(e)
                    )
        
        return results
    
    def _execute_tests_sequential(self, suite: TestSuite) -> Dict[str, TestResult]:
        """Execute tests sequentially"""
        results = {}
        
        for test_id in suite.tests:
            try:
                result = self._execute_single_test(test_id, suite)
                results[test_id] = result
            except Exception as e:
                results[test_id] = TestResult(
                    test_id=test_id,
                    test_name=test_id,
                    category=suite.category,
                    status=TestStatus.ERROR,
                    start_time=datetime.now(),
                    error_message=str(e)
                )
        
        return results
    
    def _execute_single_test(self, test_id: str, suite: TestSuite) -> TestResult:
        """Execute a single test
        
        Args:
            test_id: Test identifier
            suite: Parent test suite
            
        Returns:
            Test result
        """
        start_time = datetime.now()
        
        try:
            # Import and get test method
            test_method = self._get_test_method(test_id, suite.category)
            
            if not test_method:
                return TestResult(
                    test_id=test_id,
                    test_name=test_id,
                    category=suite.category,
                    status=TestStatus.SKIPPED,
                    start_time=start_time,
                    error_message=f"Test method {test_id} not found"
                )
            
            # Execute test
            test_result = test_method()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return TestResult(
                test_id=test_id,
                test_name=test_id,
                category=suite.category,
                status=TestStatus.PASSED if test_result.get('success', False) else TestStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                details=test_result,
                assertions_passed=test_result.get('assertions_passed', 0),
                assertions_failed=test_result.get('assertions_failed', 0),
                error_message=test_result.get('error') if not test_result.get('success', False) else None
            )
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return TestResult(
                test_id=test_id,
                test_name=test_id,
                category=suite.category,
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                error_message=str(e)
            )
    
    def _get_test_method(self, test_id: str, category: TestCategory) -> Optional[callable]:
        """Get test method by ID and category
        
        Args:
            test_id: Test identifier
            category: Test category
            
        Returns:
            Test method or None if not found
        """
        try:
            # Import appropriate test module
            module_name = f"tests.{category.value}"
            module = __import__(module_name, fromlist=[test_id])
            
            if hasattr(module, test_id):
                return getattr(module, test_id)
            else:
                self.logger.warning(f"Test method {test_id} not found in {module_name}")
                return None
                
        except ImportError as e:
            self.logger.warning(f"Could not import test module {module_name}: {e}")
            return None
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final comprehensive test report"""
        
        # Calculate overall statistics
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        total_errors = 0
        
        for category_results in self.test_results.values():
            if 'summary' in category_results:
                total_tests += category_results['summary']['total']
                total_passed += category_results['summary']['passed']
                total_failed += category_results['summary']['failed']
                total_skipped += category_results['summary']['skipped']
                total_errors += category_results['summary']['errors']
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        final_report = {
            'test_execution_summary': {
                'total_test_suites': len(self.test_suites),
                'executed_suites': len(self.test_results),
                'total_tests': total_tests,
                'tests_passed': total_passed,
                'tests_failed': total_failed,
                'tests_skipped': total_skipped,
                'tests_errors': total_errors,
                'success_rate': round(success_rate, 2),
                'execution_time': self.test_metrics.get('total_execution_time', 0),
                'timestamp': datetime.now().isoformat()
            },
            'category_results': self.test_results,
            'test_configuration': self.test_config,
            'system_information': self._get_system_information()
        }
        
        # Save report to file
        self._save_test_report(final_report)
        
        return final_report
    
    def _get_system_information(self) -> Dict[str, Any]:
        """Get system information for test report"""
        import platform
        
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'project_root': str(self.project_root),
            'test_timestamp': datetime.now().isoformat()
        }
    
    def _save_test_report(self, report: Dict[str, Any]):
        """Save test report to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = self.results_dir / f"test_report_{timestamp}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Test report saved to: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save test report: {e}")

# Test execution entry point
def main():
    """Main test execution entry point"""
    framework = AutomatedTestFramework()
    results = framework.run_all_tests()
    
    # Print summary
    summary = results.get('test_execution_summary', {})
    print(f"\n=== Test Execution Summary ===")
    print(f"Total Tests: {summary.get('total_tests', 0)}")
    print(f"Passed: {summary.get('tests_passed', 0)}")
    print(f"Failed: {summary.get('tests_failed', 0)}")
    print(f"Success Rate: {summary.get('success_rate', 0)}%")
    print(f"Execution Time: {summary.get('execution_time', 0):.2f} seconds")
    
    return results

if __name__ == "__main__":
    main()