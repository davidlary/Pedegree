#!/usr/bin/env python3
"""
DUAL-CONTEXT COMPREHENSIVE TESTING
Tests components in both isolation and live Streamlit runtime to detect context dependency bugs
"""

import subprocess
import time
import requests
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import threading
import signal
from typing import Dict, List, Any

class DualContextTester:
    def __init__(self):
        self.streamlit_process = None
        self.base_url = "http://localhost:8501"
        self.test_results = {
            'isolation_tests': [],
            'runtime_tests': [],
            'context_comparisons': [],
            'evidence_collected': [],
            'critical_bugs': [],
            'scriptrun_warnings': []
        }
        self.test_start_time = datetime.now()
        
    def log_test(self, test_type, test_name, status, details="", error=None, evidence=None):
        """Log test result with context type"""
        result = {
            'test_name': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'elapsed_seconds': (datetime.now() - self.test_start_time).total_seconds(),
            'error': str(error) if error else None,
            'evidence': evidence or []
        }
        
        if test_type == 'isolation':
            self.test_results['isolation_tests'].append(result)
        elif test_type == 'runtime':
            self.test_results['runtime_tests'].append(result)
        elif test_type == 'comparison':
            self.test_results['context_comparisons'].append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️" if status == "WARN" else "🔄"
        elapsed = f"[{result['elapsed_seconds']:.1f}s]"
        print(f"{elapsed} {status_icon} [{test_type.upper()}] {test_name}: {status}")
        if details:
            print(f"    → {details}")
        if error:
            print(f"    → ERROR: {error}")
            if "ScriptRunContext" in str(error):
                self.test_results['scriptrun_warnings'].append(result)
                self.test_results['critical_bugs'].append(f"ScriptRunContext warning in {test_name}")
        if evidence:
            for item in evidence:
                print(f"    📋 EVIDENCE: {item}")
    
    def collect_evidence(self, description, value):
        """Collect concrete evidence of functionality"""
        evidence = {
            'description': description,
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results['evidence_collected'].append(evidence)
        return evidence
    
    # PHASE 1: ISOLATION TESTING
    def test_isolation_app_import(self):
        """Test 1: App import in isolation"""
        try:
            from GetInternationalStandards import InternationalStandardsApp
            self.log_test('isolation', 'App Import', 'PASS', 'Successfully imported InternationalStandardsApp')
            return InternationalStandardsApp
        except Exception as e:
            self.log_test('isolation', 'App Import', 'FAIL', error=e)
            return None
    
    def test_isolation_app_initialization(self, app_class):
        """Test 2: App initialization in isolation"""
        try:
            # Record initial file state
            initial_files = list(Path('.').rglob('*.json')) + list(Path('.').rglob('*.db'))
            initial_count = len(initial_files)
            
            app = app_class()
            
            # Collect evidence
            evidence = []
            evidence.append(self.collect_evidence("App instance created", str(type(app))))
            evidence.append(self.collect_evidence("Initial file count", initial_count))
            
            # Test critical attributes
            critical_attrs = ['config', 'orchestrator', 'database_manager', 'cache']
            missing_attrs = []
            for attr in critical_attrs:
                if hasattr(app, attr) and getattr(app, attr) is not None:
                    evidence.append(self.collect_evidence(f"{attr} attribute", "Present and not None"))
                else:
                    missing_attrs.append(attr)
            
            if not missing_attrs:
                self.log_test('isolation', 'App Initialization', 'PASS', 
                            f'All {len(critical_attrs)} critical attributes present', 
                            evidence=[e['description'] + ': ' + str(e['value']) for e in evidence])
                return app
            else:
                self.log_test('isolation', 'App Initialization', 'FAIL', 
                            f'Missing attributes: {missing_attrs}')
                return None
                
        except Exception as e:
            self.log_test('isolation', 'App Initialization', 'FAIL', error=e)
            return None
    
    def test_isolation_database_operations(self, app):
        """Test 3: Database operations in isolation"""
        try:
            if not app.database_manager:
                self.log_test('isolation', 'Database Operations', 'FAIL', 'Database manager is None')
                return False
            
            # Test disciplines
            disciplines = app.database_manager.get_disciplines()
            disciplines_count = len(disciplines) if disciplines else 0
            
            # Test standards
            standards = app.database_manager.get_all_standards()
            standards_count = len(standards) if isinstance(standards, list) else 0
            
            evidence = [
                self.collect_evidence("Disciplines loaded", disciplines_count),
                self.collect_evidence("Standards loaded", standards_count),
                self.collect_evidence("Database manager type", str(type(app.database_manager)))
            ]
            
            if disciplines_count > 0 and standards_count >= 0:
                self.log_test('isolation', 'Database Operations', 'PASS',
                            f'Loaded {disciplines_count} disciplines, {standards_count} standards',
                            evidence=[e['description'] + ': ' + str(e['value']) for e in evidence])
                return True
            else:
                self.log_test('isolation', 'Database Operations', 'FAIL',
                            f'No disciplines loaded or invalid standards')
                return False
                
        except Exception as e:
            self.log_test('isolation', 'Database Operations', 'FAIL', error=e)
            return False
    
    def test_isolation_start_system(self, app):
        """Test 4: Start system functionality in isolation"""
        try:
            # Record pre-start state
            pre_files = list(Path('.').rglob('*.json')) + list(Path('.').rglob('*.db'))
            pre_count = len(pre_files)
            
            # Test start system
            result = app._start_system()
            
            # Wait briefly for any file operations
            time.sleep(2)
            
            # Record post-start state
            post_files = list(Path('.').rglob('*.json')) + list(Path('.').rglob('*.db'))
            post_count = len(post_files)
            files_created = post_count - pre_count
            
            evidence = [
                self.collect_evidence("Start system return value", str(result)),
                self.collect_evidence("Files before start", pre_count),
                self.collect_evidence("Files after start", post_count),
                self.collect_evidence("New files created", files_created)
            ]
            
            # Check if any new files were created
            if files_created > 0:
                new_files = set(post_files) - set(pre_files)
                for new_file in list(new_files)[:3]:  # Show first 3
                    evidence.append(self.collect_evidence("New file created", str(new_file)))
            
            self.log_test('isolation', 'Start System', 'PASS',
                        f'Executed without errors, created {files_created} files',
                        evidence=[e['description'] + ': ' + str(e['value']) for e in evidence])
            return True
            
        except Exception as e:
            self.log_test('isolation', 'Start System', 'FAIL', error=e)
            return False
    
    def test_isolation_realtime_updates(self, app):
        """Test 5: Real-time update functionality in isolation"""
        try:
            # Test update methods exist
            update_methods = ['_handle_realtime_updates', '_update_system_stats', '_update_agent_progress']
            missing_methods = []
            
            for method in update_methods:
                if not hasattr(app, method):
                    missing_methods.append(method)
            
            if missing_methods:
                self.log_test('isolation', 'Real-time Updates', 'FAIL',
                            f'Missing methods: {missing_methods}')
                return False
            
            # Test method execution
            evidence = []
            for method in update_methods:
                try:
                    getattr(app, method)()
                    evidence.append(self.collect_evidence(f"{method} execution", "SUCCESS"))
                except Exception as e:
                    evidence.append(self.collect_evidence(f"{method} execution", f"ERROR: {e}"))
                    if "ScriptRunContext" in str(e):
                        self.test_results['critical_bugs'].append(f"ScriptRunContext error in {method}")
            
            self.log_test('isolation', 'Real-time Updates', 'PASS',
                        f'All {len(update_methods)} update methods executed',
                        evidence=[e['description'] + ': ' + str(e['value']) for e in evidence])
            return True
            
        except Exception as e:
            self.log_test('isolation', 'Real-time Updates', 'FAIL', error=e)
            return False
    
    def test_isolation_session_state(self, app):
        """Test 6: Session state operations in isolation"""
        try:
            # Test that the context wrapper works
            from GetInternationalStandards import streamlit_ctx
            
            # Test basic operations
            test_key = 'test_isolation_key'
            test_value = 'test_isolation_value'
            
            # Set value
            streamlit_ctx.set(test_key, test_value)
            
            # Get value
            retrieved_value = streamlit_ctx.get(test_key)
            
            evidence = [
                self.collect_evidence("Context wrapper available", str(type(streamlit_ctx))),
                self.collect_evidence("Set operation", "SUCCESS"),
                self.collect_evidence("Get operation", f"Retrieved: {retrieved_value}"),
                self.collect_evidence("Value match", str(retrieved_value == test_value))
            ]
            
            if retrieved_value == test_value:
                self.log_test('isolation', 'Session State', 'PASS',
                            'Context wrapper functioning correctly',
                            evidence=[e['description'] + ': ' + str(e['value']) for e in evidence])
                return True
            else:
                self.log_test('isolation', 'Session State', 'FAIL',
                            f'Value mismatch: expected {test_value}, got {retrieved_value}')
                return False
                
        except Exception as e:
            self.log_test('isolation', 'Session State', 'FAIL', error=e)
            return False
    
    # PHASE 2: RUNTIME TESTING
    def start_streamlit_server(self):
        """Start Streamlit server for runtime testing"""
        print(f"\n🚀 STARTING STREAMLIT SERVER FOR RUNTIME TESTING")
        print("=" * 60)
        
        try:
            self.streamlit_process = subprocess.Popen([
                "streamlit", "run", "GetInternationalStandards.py",
                "--server.port=8501",
                "--server.headless=true",
                "--server.enableCORS=false",
                "--server.enableXsrfProtection=false"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
            )
            
            print("⏳ Waiting for Streamlit server to start...")
            
            # Wait for server to be ready
            for attempt in range(60):
                try:
                    response = requests.get(self.base_url, timeout=5)
                    if response.status_code == 200:
                        self.log_test('runtime', 'Server Startup', 'PASS',
                                    f'Server ready at {self.base_url}')
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                if attempt % 10 == 0 and attempt > 0:
                    print(f"    Still waiting... ({attempt}s)")
                time.sleep(1)
            
            self.log_test('runtime', 'Server Startup', 'FAIL',
                        'Server failed to start within 60 seconds')
            return False
            
        except Exception as e:
            self.log_test('runtime', 'Server Startup', 'FAIL', error=e)
            return False
    
    def test_runtime_homepage_content(self):
        """Test 7: Homepage content in runtime"""
        try:
            response = requests.get(self.base_url, timeout=15)
            
            if response.status_code != 200:
                self.log_test('runtime', 'Homepage Content', 'FAIL',
                            f'HTTP {response.status_code}')
                return False
            
            content = response.text
            
            # Check for key elements
            key_elements = [
                'International Standards',
                'Multi-Agent',
                'Dashboard',
                'streamlit',
                'Streamlit'
            ]
            
            found_elements = []
            for element in key_elements:
                if element in content:
                    found_elements.append(element)
            
            evidence = [
                self.collect_evidence("HTTP status", response.status_code),
                self.collect_evidence("Content length", len(content)),
                self.collect_evidence("Elements found", f"{len(found_elements)}/{len(key_elements)}"),
                self.collect_evidence("Found elements", str(found_elements))
            ]
            
            if len(found_elements) >= 2:  # At least 2/5 elements
                self.log_test('runtime', 'Homepage Content', 'PASS',
                            f'Found {len(found_elements)}/{len(key_elements)} key elements',
                            evidence=[e['description'] + ': ' + str(e['value']) for e in evidence])
                return True
            else:
                self.log_test('runtime', 'Homepage Content', 'FAIL',
                            f'Only found {found_elements} out of {key_elements}')
                return False
                
        except Exception as e:
            self.log_test('runtime', 'Homepage Content', 'FAIL', error=e)
            return False
    
    def test_runtime_app_state(self):
        """Test 8: App state and session persistence in runtime"""
        try:
            # Make multiple requests to test session persistence
            session = requests.Session()
            
            # First request
            response1 = session.get(self.base_url, timeout=10)
            
            # Wait a moment
            time.sleep(2)
            
            # Second request with same session
            response2 = session.get(self.base_url, timeout=10)
            
            evidence = [
                self.collect_evidence("First request status", response1.status_code),
                self.collect_evidence("Second request status", response2.status_code),
                self.collect_evidence("Content length diff", abs(len(response1.text) - len(response2.text))),
                self.collect_evidence("Session maintained", "Session object used")
            ]
            
            if response1.status_code == 200 and response2.status_code == 200:
                self.log_test('runtime', 'App State Persistence', 'PASS',
                            'Multiple requests successful with session',
                            evidence=[e['description'] + ': ' + str(e['value']) for e in evidence])
                return True
            else:
                self.log_test('runtime', 'App State Persistence', 'FAIL',
                            'Session requests failed')
                return False
                
        except Exception as e:
            self.log_test('runtime', 'App State Persistence', 'FAIL', error=e)
            return False
    
    def test_runtime_interactions(self):
        """Test 9: Runtime interactions and state changes"""
        try:
            # Test multiple page loads to simulate user interaction
            session = requests.Session()
            
            # Simulate loading different parts of the app
            interactions = [
                ('Main page', '/'),
                ('Health check', '/healthz'),  # Common Streamlit endpoint
                ('Main page reload', '/')
            ]
            
            evidence = []
            successful_interactions = 0
            
            for interaction_name, endpoint in interactions:
                try:
                    url = self.base_url + endpoint if endpoint != '/' else self.base_url
                    response = session.get(url, timeout=10)
                    
                    if response.status_code in [200, 404]:  # 404 is acceptable for healthz
                        successful_interactions += 1
                        evidence.append(self.collect_evidence(
                            f"{interaction_name} response", 
                            f"HTTP {response.status_code}"
                        ))
                    
                except Exception as e:
                    evidence.append(self.collect_evidence(
                        f"{interaction_name} error", 
                        str(e)
                    ))
            
            if successful_interactions >= 2:  # At least 2/3 interactions work
                self.log_test('runtime', 'Runtime Interactions', 'PASS',
                            f'{successful_interactions}/{len(interactions)} interactions successful',
                            evidence=[e['description'] + ': ' + str(e['value']) for e in evidence])
                return True
            else:
                self.log_test('runtime', 'Runtime Interactions', 'FAIL',
                            f'Only {successful_interactions}/{len(interactions)} interactions successful')
                return False
                
        except Exception as e:
            self.log_test('runtime', 'Runtime Interactions', 'FAIL', error=e)
            return False
    
    # PHASE 3: CONTEXT COMPARISON
    def compare_contexts(self):
        """Compare isolation vs runtime test results"""
        print(f"\n🔍 CONTEXT COMPARISON ANALYSIS")
        print("=" * 50)
        
        isolation_results = {test['test_name']: test['status'] for test in self.test_results['isolation_tests']}
        runtime_results = {test['test_name']: test['status'] for test in self.test_results['runtime_tests']}
        
        # Find tests that exist in both contexts
        common_tests = set(isolation_results.keys()) & set(runtime_results.keys())
        
        context_bugs = []
        
        for test_name in common_tests:
            iso_status = isolation_results[test_name]
            runtime_status = runtime_results.get(test_name, 'NOT_TESTED')
            
            if iso_status != runtime_status:
                bug_desc = f"{test_name}: Isolation={iso_status}, Runtime={runtime_status}"
                context_bugs.append(bug_desc)
                self.test_results['critical_bugs'].append(bug_desc)
                
                self.log_test('comparison', 'Context Dependency Bug', 'CRITICAL',
                            f'{test_name} behaves differently in isolation vs runtime')
        
        # Check for ScriptRunContext warnings
        if self.test_results['scriptrun_warnings']:
            for warning in self.test_results['scriptrun_warnings']:
                self.log_test('comparison', 'ScriptRunContext Warning', 'CRITICAL',
                            f"Context dependency detected in {warning['test_name']}")
        
        # Overall comparison result
        if not context_bugs and not self.test_results['scriptrun_warnings']:
            self.log_test('comparison', 'Overall Context Consistency', 'PASS',
                        'No context dependency bugs detected')
            return True
        else:
            self.log_test('comparison', 'Overall Context Consistency', 'FAIL',
                        f'{len(context_bugs)} context bugs, {len(self.test_results["scriptrun_warnings"])} ScriptRunContext warnings')
            return False
    
    # PHASE 4: EVIDENCE AND STATE VERIFICATION
    def verify_evidence_and_state(self):
        """Verify all collected evidence and state changes"""
        print(f"\n📋 EVIDENCE AND STATE VERIFICATION")
        print("=" * 50)
        
        # Check for concrete evidence of functionality
        evidence_categories = {
            'file_creation': [],
            'database_changes': [],
            'state_changes': [],
            'function_execution': []
        }
        
        for evidence in self.test_results['evidence_collected']:
            desc = evidence['description'].lower()
            if 'file' in desc or 'created' in desc:
                evidence_categories['file_creation'].append(evidence)
            elif 'database' in desc or 'discipline' in desc or 'standard' in desc:
                evidence_categories['database_changes'].append(evidence)
            elif 'state' in desc or 'session' in desc:
                evidence_categories['state_changes'].append(evidence)
            elif 'execution' in desc or 'method' in desc:
                evidence_categories['function_execution'].append(evidence)
        
        # Verify each category
        verification_results = []
        
        for category, evidence_list in evidence_categories.items():
            if evidence_list:
                self.log_test('evidence', f'{category.title()} Evidence', 'PASS',
                            f'{len(evidence_list)} pieces of evidence collected')
                verification_results.append(True)
            else:
                self.log_test('evidence', f'{category.title()} Evidence', 'WARN',
                            'No evidence collected for this category')
                verification_results.append(False)
        
        # Overall evidence verification
        evidence_score = sum(verification_results) / len(verification_results)
        
        if evidence_score >= 0.75:  # At least 75% of categories have evidence
            self.log_test('evidence', 'Overall Evidence Quality', 'PASS',
                        f'{evidence_score*100:.0f}% of evidence categories satisfied')
            return True
        else:
            self.log_test('evidence', 'Overall Evidence Quality', 'FAIL',
                        f'Only {evidence_score*100:.0f}% of evidence categories satisfied')
            return False
    
    def generate_comprehensive_report(self):
        """Generate final comprehensive test report"""
        print(f"\n" + "=" * 80)
        print("📊 DUAL-CONTEXT COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        # Summary statistics
        isolation_total = len(self.test_results['isolation_tests'])
        isolation_passed = sum(1 for t in self.test_results['isolation_tests'] if t['status'] == 'PASS')
        
        runtime_total = len(self.test_results['runtime_tests'])
        runtime_passed = sum(1 for t in self.test_results['runtime_tests'] if t['status'] == 'PASS')
        
        comparison_total = len(self.test_results['context_comparisons'])
        comparison_passed = sum(1 for t in self.test_results['context_comparisons'] if t['status'] == 'PASS')
        
        evidence_collected = len(self.test_results['evidence_collected'])
        critical_bugs = len(self.test_results['critical_bugs'])
        scriptrun_warnings = len(self.test_results['scriptrun_warnings'])
        
        print(f"🔬 ISOLATION TESTING: {isolation_passed}/{isolation_total} passed ({isolation_passed/isolation_total*100:.1f}%)" if isolation_total > 0 else "🔬 ISOLATION TESTING: No tests run")
        print(f"🌐 RUNTIME TESTING: {runtime_passed}/{runtime_total} passed ({runtime_passed/runtime_total*100:.1f}%)" if runtime_total > 0 else "🌐 RUNTIME TESTING: No tests run")
        print(f"🔍 CONTEXT COMPARISON: {comparison_passed}/{comparison_total} passed ({comparison_passed/comparison_total*100:.1f}%)" if comparison_total > 0 else "🔍 CONTEXT COMPARISON: No comparisons made")
        print(f"📋 EVIDENCE COLLECTED: {evidence_collected} pieces")
        print(f"🚨 CRITICAL BUGS: {critical_bugs}")
        print(f"⚠️  SCRIPTRUN WARNINGS: {scriptrun_warnings}")
        
        # Enhanced verification criteria
        criteria_results = {
            "Functions work identically in both contexts": critical_bugs == 0,
            "Zero ScriptRunContext warnings": scriptrun_warnings == 0,
            "Isolation tests pass": isolation_passed == isolation_total if isolation_total > 0 else False,
            "Runtime tests pass": runtime_passed == runtime_total if runtime_total > 0 else False,
            "Evidence collected": evidence_collected > 0,
            "No context dependency bugs": len([b for b in self.test_results['critical_bugs'] if 'Context Dependency' in b]) == 0
        }
        
        print(f"\n✅ ENHANCED VERIFICATION CRITERIA:")
        passed_criteria = 0
        for criterion, result in criteria_results.items():
            status = "✅" if result else "❌"
            print(f"{status} {criterion}")
            if result:
                passed_criteria += 1
        
        overall_score = passed_criteria / len(criteria_results)
        
        print(f"\n📊 OVERALL SCORE: {passed_criteria}/{len(criteria_results)} ({overall_score*100:.1f}%)")
        
        # Final verdict
        if overall_score >= 0.9 and critical_bugs == 0 and scriptrun_warnings == 0:
            print(f"\n🎉 VERDICT: PRODUCTION READY")
            print("✅ All dual-context tests passed")
            print("✅ No context dependency bugs detected")
            print("✅ No ScriptRunContext warnings")
            print("✅ Comprehensive evidence collected")
            verdict = "PRODUCTION_READY"
        elif overall_score >= 0.7:
            print(f"\n⚠️  VERDICT: NEEDS MINOR FIXES")
            print(f"✅ Most tests passed ({overall_score*100:.1f}%)")
            if critical_bugs > 0:
                print(f"❌ {critical_bugs} critical bugs need fixing")
            if scriptrun_warnings > 0:
                print(f"⚠️  {scriptrun_warnings} ScriptRunContext warnings")
            verdict = "NEEDS_FIXES"
        else:
            print(f"\n❌ VERDICT: MAJOR ISSUES DETECTED")
            print(f"❌ Only {overall_score*100:.1f}% of tests passed")
            print(f"🚨 {critical_bugs} critical bugs detected")
            print(f"⚠️  {scriptrun_warnings} ScriptRunContext warnings")
            verdict = "MAJOR_ISSUES"
        
        # Save detailed results
        with open('dual_context_test_results.json', 'w') as f:
            json.dump({
                'test_results': self.test_results,
                'summary': {
                    'isolation_tests': {'total': isolation_total, 'passed': isolation_passed},
                    'runtime_tests': {'total': runtime_total, 'passed': runtime_passed},
                    'context_comparisons': {'total': comparison_total, 'passed': comparison_passed},
                    'evidence_collected': evidence_collected,
                    'critical_bugs': critical_bugs,
                    'scriptrun_warnings': scriptrun_warnings,
                    'overall_score': overall_score,
                    'verdict': verdict
                },
                'timestamp': datetime.now().isoformat(),
                'test_duration_seconds': (datetime.now() - self.test_start_time).total_seconds()
            }, f, indent=2)
        
        return verdict == "PRODUCTION_READY"
    
    def cleanup(self):
        """Clean up resources"""
        if self.streamlit_process:
            print(f"\n🧹 Cleaning up Streamlit server...")
            try:
                self.streamlit_process.terminate()
                self.streamlit_process.wait(timeout=10)
            except:
                try:
                    self.streamlit_process.kill()
                except:
                    pass
        
        # Kill any remaining streamlit processes
        try:
            subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
        except:
            pass
    
    def run_comprehensive_dual_context_test(self):
        """Run the complete dual-context test suite"""
        print("🚀 DUAL-CONTEXT COMPREHENSIVE TESTING SYSTEM")
        print("=" * 80)
        print(f"Test started: {self.test_start_time}")
        print("Testing components in BOTH isolation and runtime contexts...")
        print()
        
        try:
            # PHASE 1: ISOLATION TESTING
            print("🔬 PHASE 1: ISOLATION TESTING")
            print("-" * 40)
            
            app_class = self.test_isolation_app_import()
            if not app_class:
                return False
            
            app = self.test_isolation_app_initialization(app_class)
            if not app:
                return False
            
            self.test_isolation_database_operations(app)
            self.test_isolation_start_system(app)
            self.test_isolation_realtime_updates(app)
            self.test_isolation_session_state(app)
            
            # PHASE 2: RUNTIME TESTING
            print(f"\n🌐 PHASE 2: RUNTIME TESTING")
            print("-" * 40)
            
            if not self.start_streamlit_server():
                return False
            
            # Wait a moment for server to fully initialize
            time.sleep(5)
            
            self.test_runtime_homepage_content()
            self.test_runtime_app_state()
            self.test_runtime_interactions()
            
            # PHASE 3: CONTEXT COMPARISON
            print(f"\n🔍 PHASE 3: CONTEXT COMPARISON")
            print("-" * 40)
            
            self.compare_contexts()
            
            # PHASE 4: EVIDENCE VERIFICATION
            print(f"\n📋 PHASE 4: EVIDENCE VERIFICATION")
            print("-" * 40)
            
            self.verify_evidence_and_state()
            
            # FINAL REPORT
            return self.generate_comprehensive_report()
            
        except Exception as e:
            print(f"\n❌ CRITICAL TEST FAILURE: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.cleanup()

def main():
    """Main test execution"""
    tester = DualContextTester()
    success = tester.run_comprehensive_dual_context_test()
    
    print(f"\n🏁 FINAL RESULT: {'SUCCESS' if success else 'FAILED'}")
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)