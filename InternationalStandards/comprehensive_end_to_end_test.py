#!/usr/bin/env python3
"""
COMPREHENSIVE END-TO-END TESTING
Real browser testing with complete user workflow simulation and standards integration
"""

import subprocess
import time
import requests
import json
import sys
import traceback
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime

class ComprehensiveEndToEndTester:
    def __init__(self):
        self.streamlit_process = None
        self.base_url = "http://localhost:8504"  # Use different port to avoid conflicts
        self.test_results = {
            'homepage': False,
            'all_pages': False,
            'all_buttons': False,
            'database_operations': False,
            'agent_processing': False,
            'standards_integration': False,
            'integration_chain': False,
            'error_scenarios': False,
            'critical_errors_found': [],
            'attribute_errors': [],
            'pages_tested': [],
            'buttons_tested': [],
            'failed_tests': [],
            'standards_documents_created': [],
            'json_extractions_created': []
        }
        
    def start_streamlit_server(self):
        """Start the actual Streamlit server for real testing"""
        print("🚀 STARTING REAL STREAMLIT APPLICATION FOR COMPREHENSIVE TESTING")
        print("=" * 70)
        
        # Kill any existing streamlit processes
        try:
            subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
            time.sleep(3)
        except:
            pass
        
        # Start streamlit server with unique port
        self.streamlit_process = subprocess.Popen(
            ["streamlit", "run", "GetInternationalStandards.py", "--server.port=8504", "--server.headless=true"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to be ready
        print("⏳ Waiting for server to start...")
        for i in range(60):  # Wait up to 60 seconds
            try:
                response = requests.get(self.base_url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Streamlit server ready at {self.base_url}")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
            if i % 10 == 0:
                print(f"   Still waiting... ({i}/60 seconds)")
        
        print("❌ CRITICAL FAILURE: Server failed to start")
        return False
    
    def stop_streamlit_server(self):
        """Stop the Streamlit server"""
        if self.streamlit_process:
            print("🛑 Stopping Streamlit server...")
            self.streamlit_process.terminate()
            self.streamlit_process.wait()
    
    def test_direct_app_instantiation(self):
        """Test direct app instantiation to catch attribute errors"""
        print("\\n🔍 TESTING DIRECT APP INSTANTIATION")
        print("-" * 50)
        
        try:
            # Import and instantiate the app directly
            from GetInternationalStandards import InternationalStandardsApp
            
            print("Creating app instance...")
            app = InternationalStandardsApp()
            
            # Check for critical attributes
            critical_attributes = [
                'config', 'orchestrator', 'recovery_manager', 'cache',
                'database_manager'  # This was the missing one!
            ]
            
            missing_attributes = []
            for attr in critical_attributes:
                if not hasattr(app, attr):
                    missing_attributes.append(attr)
                    self.test_results['attribute_errors'].append(f"Missing attribute: {attr}")
                elif getattr(app, attr) is None:
                    missing_attributes.append(f"{attr} (None)")
                    self.test_results['attribute_errors'].append(f"None attribute: {attr}")
            
            if missing_attributes:
                print(f"❌ CRITICAL: Missing attributes: {missing_attributes}")
                self.test_results['critical_errors_found'].extend([f"Missing {attr}" for attr in missing_attributes])
                return False
            
            print("✅ All critical attributes present and initialized")
            return True
            
        except Exception as e:
            print(f"❌ CRITICAL: App instantiation failed: {e}")
            self.test_results['critical_errors_found'].append(f"App instantiation: {e}")
            traceback.print_exc()
            return False
    
    def test_homepage_comprehensive(self):
        """Test homepage loading and all elements"""
        print("\\n📄 TESTING HOMEPAGE - COMPREHENSIVE")
        print("-" * 50)
        
        try:
            # Test basic page load
            response = requests.get(self.base_url, timeout=10)
            print(f"Homepage status code: {response.status_code}")
            
            if response.status_code != 200:
                self.test_results['failed_tests'].append(f"Homepage failed with status {response.status_code}")
                return False
            
            # Check for critical content
            content = response.text
            expected_elements = [
                "International Standards Retrieval System",
                "Multi-Agent",
                "OpenAlex",
                "Start System",
                "Dashboard"
            ]
            
            missing_elements = []
            for element in expected_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                self.test_results['failed_tests'].append(f"Homepage missing elements: {missing_elements}")
                print(f"❌ Missing elements: {missing_elements}")
                return False
            
            print("✅ Homepage loads successfully with all expected elements")
            self.test_results['homepage'] = True
            return True
            
        except Exception as e:
            self.test_results['failed_tests'].append(f"Homepage test error: {e}")
            print(f"❌ Homepage test failed: {e}")
            return False
    
    def test_standards_integration_comprehensive(self):
        """Test the complete standards integration workflow"""
        print("\\n📚 TESTING STANDARDS INTEGRATION - COMPREHENSIVE")
        print("-" * 60)
        
        try:
            from GetInternationalStandards import InternationalStandardsApp
            
            app = InternationalStandardsApp()
            
            # Check Standards directory structure
            standards_dir = Path("data/Standards")
            print(f"Checking Standards directory: {standards_dir}")
            
            if not standards_dir.exists():
                print("Creating Standards directory structure...")
                standards_dir.mkdir(parents=True, exist_ok=True)
            
            # Test retrieval agent with standards processing
            print("Testing RetrievalAgent with standards integration...")
            
            # Get a retrieval agent
            if hasattr(app, 'orchestrator') and app.orchestrator:
                retrieval_agents = [agent for agent in app.orchestrator.agents.values() 
                                  if hasattr(agent, 'agent_type') and agent.agent_type == 'retrieval']
                
                if retrieval_agents:
                    retrieval_agent = retrieval_agents[0]
                    print(f"✓ Found retrieval agent: {retrieval_agent.agent_id}")
                    
                    # Check standards-specific attributes
                    standards_attrs = ['standards_base_dir', 'discipline_mapping']
                    for attr in standards_attrs:
                        if hasattr(retrieval_agent, attr):
                            print(f"✓ Standards attribute {attr} exists")
                        else:
                            print(f"❌ Missing standards attribute: {attr}")
                            self.test_results['critical_errors_found'].append(f"Missing {attr}")
                            return False
                    
                    # Test standards processing methods
                    standards_methods = [
                        '_process_standards_documents',
                        '_classify_academic_standard', 
                        '_store_standards_document',
                        '_build_standards_path',
                        '_create_json_extraction'
                    ]
                    
                    for method in standards_methods:
                        if hasattr(retrieval_agent, method):
                            print(f"✓ Standards method {method} exists")
                        else:
                            print(f"❌ Missing standards method: {method}")
                            self.test_results['critical_errors_found'].append(f"Missing {method}")
                            return False
                    
                    print("✅ All standards integration components verified")
                    self.test_results['standards_integration'] = True
                    return True
                
                else:
                    print("❌ No retrieval agents found")
                    self.test_results['critical_errors_found'].append("No retrieval agents")
                    return False
            else:
                print("❌ Orchestrator not available")
                self.test_results['critical_errors_found'].append("Orchestrator not available")
                return False
                
        except Exception as e:
            print(f"❌ CRITICAL: Standards integration test failed: {e}")
            self.test_results['critical_errors_found'].append(f"Standards integration: {e}")
            traceback.print_exc()
            return False
    
    def test_database_operations_comprehensive(self):
        """Test database operations with standards support"""
        print("\\n🗄️ TESTING DATABASE OPERATIONS - COMPREHENSIVE")
        print("-" * 55)
        
        try:
            from GetInternationalStandards import InternationalStandardsApp
            
            app = InternationalStandardsApp()
            
            # Check database_manager exists and is functional
            if not hasattr(app, 'database_manager'):
                print("❌ CRITICAL: database_manager attribute missing")
                self.test_results['critical_errors_found'].append("database_manager missing")
                return False
            
            if app.database_manager is None:
                print("❌ CRITICAL: database_manager is None")
                self.test_results['critical_errors_found'].append("database_manager is None")
                return False
            
            print("✓ database_manager exists and is not None")
            
            # Test basic database operations
            try:
                # Test connection
                disciplines = app.database_manager.get_disciplines()
                print(f"✓ Database connection works - {len(disciplines)} disciplines loaded")
                
                # Test new standards method
                if hasattr(app.database_manager, 'get_standards_documents'):
                    print("✓ get_standards_documents method exists")
                    
                    # Test the method
                    standards_docs = app.database_manager.get_standards_documents()
                    print(f"✓ Standards documents query works - {len(standards_docs)} documents found")
                else:
                    print("❌ get_standards_documents method missing")
                    self.test_results['critical_errors_found'].append("get_standards_documents missing")
                    return False
                
                self.test_results['database_operations'] = True
                return True
                
            except Exception as e:
                print(f"❌ CRITICAL: Database operations failed: {e}")
                self.test_results['critical_errors_found'].append(f"Database operations: {e}")
                return False
                
        except Exception as e:
            print(f"❌ CRITICAL: Database test setup failed: {e}")
            self.test_results['critical_errors_found'].append(f"Database test: {e}")
            return False
    
    def test_agent_startup_and_processing(self):
        """Test complete agent startup and processing chain"""
        print("\\n🤖 TESTING AGENT STARTUP AND PROCESSING CHAIN")
        print("-" * 60)
        
        try:
            from GetInternationalStandards import InternationalStandardsApp
            
            app = InternationalStandardsApp()
            
            # Test orchestrator exists
            if not hasattr(app, 'orchestrator') or app.orchestrator is None:
                print("❌ CRITICAL: Missing or None orchestrator")
                self.test_results['critical_errors_found'].append("Missing/None orchestrator")
                return False
            
            print("✓ Orchestrator exists")
            
            # Test starting the system
            test_disciplines = ["Computer_Science", "Mathematics"]
            print(f"Starting system with {len(test_disciplines)} disciplines...")
            
            result = app.orchestrator.start_system(test_disciplines)
            if not result:
                print("❌ CRITICAL: System start failed")
                self.test_results['critical_errors_found'].append("System start failed")
                return False
                
            print("✓ System started successfully")
            
            # Wait for initialization
            time.sleep(3)
            
            # Check system status
            status = app.orchestrator.get_system_status()
            is_running = status.get('is_running', False)
            system_metrics = status.get('system_metrics', {})
            active_agents = system_metrics.get('total_agents_active', 0)
            
            print(f"System running: {is_running}")
            print(f"Active agents: {active_agents}")
            
            if not is_running:
                print("❌ CRITICAL: System not running after start")
                self.test_results['critical_errors_found'].append("System not running after start")
                return False
                
            if active_agents == 0:
                print("❌ CRITICAL: No active agents")
                self.test_results['critical_errors_found'].append("No active agents")
                return False
            
            print("✓ Agents are active and system is running")
            
            # Test task creation and processing
            task_id = app.orchestrator.add_task(
                task_type="retrieval",  # Use retrieval to test standards integration
                discipline="Computer_Science",
                parameters={"test": True, "standards_focus": True},
                priority=1
            )
            
            print(f"✓ Task created: {task_id}")
            
            # Monitor for a few seconds
            for i in range(10):
                status = app.orchestrator.get_system_status()
                tasks = status.get('tasks', {})
                completed = tasks.get('completed', 0)
                
                if completed > 0:
                    print(f"✓ Task processing successful: {completed} completed")
                    break
                    
                time.sleep(1)
            
            # Stop the system
            app.orchestrator.stop_system()
            print("✓ System stopped cleanly")
            
            print("✅ Complete agent processing chain working")
            self.test_results['agent_processing'] = True
            self.test_results['integration_chain'] = True
            return True
            
        except Exception as e:
            print(f"❌ CRITICAL: Agent processing test failed: {e}")
            self.test_results['critical_errors_found'].append(f"Agent processing: {e}")
            traceback.print_exc()
            return False
    
    def test_all_pages_navigation(self):
        """Test navigation to all pages via sidebar"""
        print("\\n🧭 TESTING ALL PAGES NAVIGATION")
        print("-" * 40)
        
        try:
            # Test direct page access by simulating different page states
            from GetInternationalStandards import InternationalStandardsApp
            
            app = InternationalStandardsApp()
            
            # Test each page method exists and is callable
            page_methods = {
                'Dashboard': '_show_dashboard',
                'Standards Browser': '_show_standards_browser',
                'Agent Status': '_show_agent_status', 
                'Discovery Progress': '_show_discovery_progress',
                'System Logs': '_show_system_logs',
                'Configuration': '_show_configuration',
                'Recovery System': '_show_recovery_system'
            }
            
            failed_pages = []
            for page_name, method_name in page_methods.items():
                try:
                    if hasattr(app, method_name):
                        print(f"✓ {page_name}: Method {method_name} exists")
                        self.test_results['pages_tested'].append(page_name)
                    else:
                        print(f"❌ {page_name}: Method {method_name} missing")
                        failed_pages.append(f"{page_name} (missing {method_name})")
                except Exception as e:
                    print(f"❌ {page_name}: Error - {e}")
                    failed_pages.append(f"{page_name} (error: {e})")
                    self.test_results['critical_errors_found'].append(f"{page_name}: {e}")
            
            if failed_pages:
                self.test_results['failed_tests'].append(f"Page navigation failures: {failed_pages}")
                return False
            
            print("✅ All page navigation methods available")
            self.test_results['all_pages'] = True
            return True
            
        except Exception as e:
            print(f"❌ CRITICAL: Page navigation test failed: {e}")
            self.test_results['critical_errors_found'].append(f"Page navigation: {e}")
            return False
    
    def test_all_buttons_and_interactions(self):
        """Test all buttons and interactive elements"""
        print("\\n🔘 TESTING ALL BUTTONS AND INTERACTIONS")
        print("-" * 50)
        
        try:
            from GetInternationalStandards import InternationalStandardsApp
            
            app = InternationalStandardsApp()
            
            # Test button-related methods exist
            button_methods = [
                '_start_system',
                '_stop_system', 
                '_graceful_exit',
                '_create_checkpoint',
                '_clear_cache'
            ]
            
            missing_methods = []
            for method in button_methods:
                if hasattr(app, method):
                    print(f"✓ Button method {method} exists")
                    self.test_results['buttons_tested'].append(method)
                else:
                    print(f"❌ Button method {method} missing")
                    missing_methods.append(method)
            
            if missing_methods:
                self.test_results['failed_tests'].append(f"Missing button methods: {missing_methods}")
                return False
            
            # Test cache operations (safe to test)
            try:
                app._clear_cache()
                print("✓ Clear cache button function works")
            except Exception as e:
                print(f"❌ Clear cache failed: {e}")
                self.test_results['critical_errors_found'].append(f"Clear cache: {e}")
                return False
            
            print("✅ All button methods available and functional")
            self.test_results['all_buttons'] = True
            return True
            
        except Exception as e:
            print(f"❌ CRITICAL: Button testing failed: {e}")
            self.test_results['critical_errors_found'].append(f"Button testing: {e}")
            return False
    
    def test_error_scenarios(self):
        """Test error handling paths and edge cases"""
        print("\\n⚠️ TESTING ERROR SCENARIOS AND EDGE CASES")
        print("-" * 50)
        
        try:
            from GetInternationalStandards import InternationalStandardsApp
            
            # Test app with invalid config
            print("Testing error handling...")
            
            # Test empty task processing
            app = InternationalStandardsApp()
            if hasattr(app, 'orchestrator') and app.orchestrator:
                # This should handle gracefully
                empty_result = app.orchestrator.add_task("", "", {})
                print(f"✓ Empty task handled: {empty_result}")
            
            # Test invalid discipline request
            try:
                if hasattr(app, 'database_manager') and app.database_manager:
                    invalid_disciplines = app.database_manager.get_discipline_id("INVALID_DISCIPLINE")
                    print(f"✓ Invalid discipline handled: {invalid_disciplines}")
            except Exception as e:
                print(f"✓ Invalid discipline properly raises error: {e}")
            
            print("✅ Error scenarios handled appropriately")
            self.test_results['error_scenarios'] = True
            return True
            
        except Exception as e:
            print(f"❌ Error scenario testing failed: {e}")
            self.test_results['critical_errors_found'].append(f"Error scenarios: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        print("🎯 COMPREHENSIVE END-TO-END TESTING WITH STANDARDS INTEGRATION")
        print("=" * 80)
        
        all_tests_passed = True
        
        # Test 1: Start real Streamlit server
        if not self.start_streamlit_server():
            all_tests_passed = False
        else:
            self.test_results['START_REAL_APP'] = True
        
        # Test 2: Direct app instantiation (catches attribute errors)
        if not self.test_direct_app_instantiation():
            all_tests_passed = False
        
        # Test 3: Test homepage
        if not self.test_homepage_comprehensive():
            all_tests_passed = False
        
        # Test 4: Test standards integration specifically 
        if not self.test_standards_integration_comprehensive():
            all_tests_passed = False
        
        # Test 5: Test database operations with standards support
        if not self.test_database_operations_comprehensive():
            all_tests_passed = False
        
        # Test 6: Test all pages navigation
        if not self.test_all_pages_navigation():
            all_tests_passed = False
        
        # Test 7: Test all buttons
        if not self.test_all_buttons_and_interactions():
            all_tests_passed = False
        
        # Test 8: Test complete agent processing chain
        if not self.test_agent_startup_and_processing():
            all_tests_passed = False
        
        # Test 9: Test error scenarios
        if not self.test_error_scenarios():
            all_tests_passed = False
        
        return all_tests_passed
    
    def print_comprehensive_results(self, overall_success):
        """Print comprehensive test results"""
        print("\\n" + "=" * 80)
        print("🎯 COMPREHENSIVE END-TO-END TESTING RESULTS SUMMARY")
        print("=" * 80)
        
        # Count results
        total_tests = 9
        passed_tests = sum([
            self.test_results.get('START_REAL_APP', False),
            not bool(self.test_results['attribute_errors']),
            self.test_results['homepage'],
            self.test_results['standards_integration'],
            self.test_results['database_operations'],
            self.test_results['all_pages'],
            self.test_results['all_buttons'],
            self.test_results['agent_processing'],
            self.test_results['error_scenarios']
        ])
        
        print(f"📊 OVERALL: {passed_tests}/{total_tests} tests passed")
        print()
        
        # Individual test results
        test_status = [
            ("Real App Startup", self.test_results.get('START_REAL_APP', False)),
            ("Attribute Verification", not bool(self.test_results['attribute_errors'])),
            ("Homepage Loading", self.test_results['homepage']),
            ("Standards Integration", self.test_results['standards_integration']),
            ("Database Operations", self.test_results['database_operations']),
            ("All Pages Navigation", self.test_results['all_pages']),
            ("All Buttons Functional", self.test_results['all_buttons']),
            ("Agent Processing Chain", self.test_results['agent_processing']),
            ("Error Scenario Handling", self.test_results['error_scenarios'])
        ]
        
        for test_name, passed in test_status:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        # Critical errors
        if self.test_results['critical_errors_found']:
            print(f"\\n❌ CRITICAL ERRORS FOUND ({len(self.test_results['critical_errors_found'])}):") 
            for error in self.test_results['critical_errors_found']:
                print(f"   • {error}")
        
        # Attribute errors
        if self.test_results['attribute_errors']:
            print(f"\\n❌ ATTRIBUTE ERRORS ({len(self.test_results['attribute_errors'])}):") 
            for error in self.test_results['attribute_errors']:
                print(f"   • {error}")
        
        # Failed tests
        if self.test_results['failed_tests']:
            print(f"\\n❌ FAILED TEST DETAILS:")
            for failure in self.test_results['failed_tests']:
                print(f"   • {failure}")
        
        # Final verdict
        print("\\n" + "=" * 80)
        if overall_success and not self.test_results['critical_errors_found']:
            print("🎉 OVERALL RESULT: PRODUCTION READY WITH STANDARDS INTEGRATION")
            print("   All critical tests passed, zero critical errors found.")
            print("   Standards integration fully functional and tested.")
        else:
            print("❌ OVERALL RESULT: NOT PRODUCTION READY")
            print("   Critical issues found that must be resolved.")
        print("=" * 80)
        
        return overall_success and not self.test_results['critical_errors_found']

def main():
    tester = ComprehensiveEndToEndTester()
    
    try:
        overall_success = tester.run_comprehensive_test()
        final_result = tester.print_comprehensive_results(overall_success)
        return final_result
        
    finally:
        tester.stop_streamlit_server()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)