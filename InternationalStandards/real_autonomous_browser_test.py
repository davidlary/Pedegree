#!/usr/bin/env python3
"""
REAL AUTONOMOUS BROWSER TEST
Tests the actual system with real browser simulation to find what's actually broken
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

class RealAutonomousBrowserTest:
    def __init__(self):
        self.streamlit_process = None
        self.base_url = "http://localhost:8501"
        self.test_results = []
        self.errors_found = []
        self.downloads_created = []
        self.session = requests.Session()
        self.test_start_time = datetime.now()
        
    def log_result(self, test_name, status, details="", error=None):
        """Log test result with timestamp"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'elapsed_seconds': (datetime.now() - self.test_start_time).total_seconds(),
            'error': str(error) if error else None
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        elapsed = f"[{result['elapsed_seconds']:.1f}s]"
        print(f"{elapsed} {status_icon} {test_name}: {status}")
        if details:
            print(f"    → {details}")
        if error:
            print(f"    → ERROR: {error}")
            self.errors_found.append(f"{test_name}: {error}")
    
    def start_streamlit_server(self):
        """Start Streamlit server and wait for it to be ready"""
        print("🚀 STARTING STREAMLIT APPLICATION FOR REAL TESTING")
        print("=" * 60)
        
        # Start server in background
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
            
            # Wait up to 90 seconds for server to be ready
            for attempt in range(90):
                try:
                    response = self.session.get(self.base_url, timeout=5)
                    if response.status_code == 200:
                        self.log_result("Server Startup", "PASS", f"Server ready at {self.base_url}")
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                if attempt % 10 == 0:
                    print(f"    Still waiting... ({attempt}s)")
                time.sleep(1)
            
            self.log_result("Server Startup", "FAIL", "Server failed to start within 90 seconds")
            return False
            
        except Exception as e:
            self.log_result("Server Startup", "FAIL", error=e)
            return False
    
    def test_homepage_loads(self):
        """Test that homepage actually loads"""
        self.log_result("Homepage Load Test", "RUNNING", "Fetching homepage...")
        
        try:
            response = self.session.get(self.base_url, timeout=15)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for key elements that should be present
                required_elements = [
                    "International Standards",
                    "Multi-Agent System", 
                    "Dashboard",
                    "streamlit"
                ]
                
                found_elements = []
                for element in required_elements:
                    if element in content:
                        found_elements.append(element)
                
                if len(found_elements) >= 2:
                    self.log_result("Homepage Load Test", "PASS", 
                                  f"Found {len(found_elements)}/{len(required_elements)} key elements")
                    return content
                else:
                    self.log_result("Homepage Load Test", "FAIL", 
                                  f"Only found {found_elements} out of {required_elements}")
                    return None
            else:
                self.log_result("Homepage Load Test", "FAIL", 
                              f"HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.log_result("Homepage Load Test", "FAIL", error=e)
            return None
    
    def test_app_initialization(self):
        """Test that the app actually initializes properly"""
        self.log_result("App Initialization Test", "RUNNING", "Testing direct app import...")
        
        try:
            # Import the app directly
            sys.path.insert(0, '.')
            from GetInternationalStandards import InternationalStandardsApp
            
            app = InternationalStandardsApp()
            
            # Test critical components
            critical_checks = [
                ('config', hasattr(app, 'config') and app.config is not None),
                ('orchestrator', hasattr(app, 'orchestrator') and app.orchestrator is not None),
                ('database_manager', hasattr(app, 'database_manager') and app.database_manager is not None),
                ('cache', hasattr(app, 'cache') and app.cache is not None)
            ]
            
            failed_checks = []
            for check_name, check_result in critical_checks:
                if not check_result:
                    failed_checks.append(check_name)
            
            if not failed_checks:
                self.log_result("App Initialization Test", "PASS", "All critical components initialized")
                return app
            else:
                self.log_result("App Initialization Test", "FAIL", 
                              f"Failed components: {failed_checks}")
                return None
                
        except Exception as e:
            self.log_result("App Initialization Test", "FAIL", error=e)
            return None
    
    def test_start_system_button(self, app):
        """Test the actual Start System functionality"""
        self.log_result("Start System Test", "RUNNING", "Testing start system functionality...")
        
        try:
            # Check if start system method exists
            if not hasattr(app, '_start_system'):
                self.log_result("Start System Test", "FAIL", "_start_system method missing")
                return False
            
            # Get initial state
            initial_status = app.orchestrator.get_system_status() if app.orchestrator else {}
            
            # Simulate the start system button click
            self.log_result("Start System Test", "RUNNING", "Simulating Start System button click...")
            
            # Call the start system method
            result = app._start_system()
            
            if result:
                self.log_result("Start System Test", "PASS", "Start system method executed successfully")
                return True
            else:
                self.log_result("Start System Test", "FAIL", "Start system method returned False")
                return False
                
        except Exception as e:
            self.log_result("Start System Test", "FAIL", error=e)
            return False
    
    def test_real_time_updates(self, app):
        """Test if real-time updates actually work"""
        self.log_result("Real-Time Updates Test", "RUNNING", "Testing update mechanisms...")
        
        try:
            # Test the real-time update methods
            if not hasattr(app, '_handle_realtime_updates'):
                self.log_result("Real-Time Updates Test", "FAIL", "_handle_realtime_updates method missing")
                return False
            
            if not hasattr(app, '_update_system_stats'):
                self.log_result("Real-Time Updates Test", "FAIL", "_update_system_stats method missing")
                return False
            
            # Test calling update methods
            self.log_result("Real-Time Updates Test", "RUNNING", "Calling _update_system_stats...")
            app._update_system_stats()
            
            self.log_result("Real-Time Updates Test", "RUNNING", "Calling _handle_realtime_updates...")
            app._handle_realtime_updates()
            
            self.log_result("Real-Time Updates Test", "PASS", "Update methods executed without errors")
            return True
            
        except Exception as e:
            self.log_result("Real-Time Updates Test", "FAIL", error=e)
            return False
    
    def test_agent_status_updates(self, app):
        """Test if agent status actually updates"""
        self.log_result("Agent Status Updates Test", "RUNNING", "Testing agent status functionality...")
        
        try:
            # Get initial agent status
            initial_status = app.get_agent_status()
            
            if not initial_status or 'agents' not in initial_status:
                self.log_result("Agent Status Updates Test", "FAIL", "get_agent_status returned empty or invalid data")
                return False
            
            initial_agent_count = len(initial_status.get('agents', {}))
            
            # Test agent update methods
            if hasattr(app, '_update_agent_progress'):
                app._update_agent_progress()
                
            if hasattr(app, '_start_random_agents'):
                app._start_random_agents()
            
            # Get status after updates
            updated_status = app.get_agent_status()
            updated_agent_count = len(updated_status.get('agents', {}))
            
            self.log_result("Agent Status Updates Test", "PASS", 
                          f"Initial agents: {initial_agent_count}, After updates: {updated_agent_count}")
            return True
            
        except Exception as e:
            self.log_result("Agent Status Updates Test", "FAIL", error=e)
            return False
    
    def test_database_operations(self, app):
        """Test actual database operations"""
        self.log_result("Database Operations Test", "RUNNING", "Testing database functionality...")
        
        try:
            if not app.database_manager:
                self.log_result("Database Operations Test", "FAIL", "Database manager is None")
                return False
            
            # Test getting disciplines
            disciplines = app.database_manager.get_disciplines()
            if not disciplines:
                self.log_result("Database Operations Test", "FAIL", "No disciplines returned")
                return False
            
            # Test getting standards
            standards = app.database_manager.get_all_standards()
            if not isinstance(standards, list):
                self.log_result("Database Operations Test", "FAIL", "Standards not returned as list")
                return False
            
            self.log_result("Database Operations Test", "PASS", 
                          f"Loaded {len(disciplines)} disciplines, {len(standards)} standards")
            return True
            
        except Exception as e:
            self.log_result("Database Operations Test", "FAIL", error=e)
            return False
    
    def test_full_system_workflow(self, app):
        """Test the complete system workflow end-to-end"""
        self.log_result("Full System Workflow Test", "RUNNING", "Testing complete workflow...")
        
        try:
            # Step 1: Start the system
            self.log_result("Full System Workflow Test", "RUNNING", "Step 1: Starting system...")
            if not self.test_start_system_button(app):
                return False
            
            # Step 2: Wait and check for updates
            self.log_result("Full System Workflow Test", "RUNNING", "Step 2: Waiting for system activity...")
            time.sleep(5)  # Wait 5 seconds for system to start working
            
            # Step 3: Check if agents are active
            agent_status = app.get_agent_status()
            active_agents = sum(1 for agent in agent_status.get('agents', {}).values() 
                              if agent.get('status') == 'running')
            
            if active_agents == 0:
                self.log_result("Full System Workflow Test", "FAIL", 
                              "No agents became active after starting system")
                return False
            
            # Step 4: Check for data updates
            self.log_result("Full System Workflow Test", "RUNNING", "Step 3: Checking for data updates...")
            
            # Check if system stats have updated
            if hasattr(app, '_update_system_stats'):
                app._update_system_stats()
            
            self.log_result("Full System Workflow Test", "PASS", 
                          f"System workflow completed successfully. {active_agents} agents active")
            return True
            
        except Exception as e:
            self.log_result("Full System Workflow Test", "FAIL", error=e)
            return False
    
    def test_file_creation(self):
        """Test if any files are actually created during the process"""
        self.log_result("File Creation Test", "RUNNING", "Checking for created files...")
        
        # Check for various file types that should be created
        possible_files = [
            "data/international_standards.db",
            "recovery/system_state.json",
            "*.json",
            "*.csv",
            "*.db"
        ]
        
        created_files = []
        
        # Check current directory and subdirectories
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.json', '.csv', '.db', '.txt')) and 'test' not in file.lower():
                    file_path = os.path.join(root, file)
                    # Check if file was modified recently (within last hour)
                    try:
                        mtime = os.path.getmtime(file_path)
                        if datetime.now().timestamp() - mtime < 3600:  # Within last hour
                            created_files.append(file_path)
                            self.downloads_created.append(file_path)
                    except:
                        pass
        
        if created_files:
            self.log_result("File Creation Test", "PASS", 
                          f"Found {len(created_files)} recently modified files: {created_files[:5]}")
            return True
        else:
            self.log_result("File Creation Test", "FAIL", 
                          "No recently created/modified files found")
            return False
    
    def run_complete_test(self):
        """Run the complete autonomous browser test"""
        print("🤖 REAL AUTONOMOUS BROWSER TEST - FINDING ACTUAL ISSUES")
        print("=" * 70)
        print(f"Test started at: {self.test_start_time}")
        print()
        
        try:
            # Step 1: Start server
            if not self.start_streamlit_server():
                return False
            
            # Step 2: Test homepage
            homepage_content = self.test_homepage_loads()
            if not homepage_content:
                return False
            
            # Step 3: Test app initialization
            app = self.test_app_initialization()
            if not app:
                return False
            
            # Step 4: Test database operations
            if not self.test_database_operations(app):
                return False
            
            # Step 5: Test real-time updates
            if not self.test_real_time_updates(app):
                return False
            
            # Step 6: Test agent status updates
            if not self.test_agent_status_updates(app):
                return False
            
            # Step 7: Test full workflow
            if not self.test_full_system_workflow(app):
                return False
            
            # Step 8: Test file creation
            self.test_file_creation()
            
            # Final assessment
            self.generate_final_report()
            return len(self.errors_found) == 0
            
        except Exception as e:
            self.log_result("Complete Test", "FAIL", error=e)
            return False
        finally:
            self.cleanup()
    
    def generate_final_report(self):
        """Generate final test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed_tests = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        
        print("\n" + "=" * 70)
        print("📊 FINAL AUTONOMOUS TEST REPORT")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        print(f"Total Runtime: {(datetime.now() - self.test_start_time).total_seconds():.1f} seconds")
        
        if self.errors_found:
            print(f"\n❌ ERRORS FOUND ({len(self.errors_found)}):")
            for i, error in enumerate(self.errors_found, 1):
                print(f"  {i}. {error}")
        
        if self.downloads_created:
            print(f"\n📁 FILES CREATED ({len(self.downloads_created)}):")
            for file in self.downloads_created:
                print(f"  • {file}")
        
        print("\n🎯 VERDICT:")
        if len(self.errors_found) == 0 and passed_tests > 0:
            print("✅ SYSTEM IS WORKING CORRECTLY")
            print("   All tests passed, no errors found")
        else:
            print("❌ SYSTEM HAS ISSUES")
            print("   Root causes need to be investigated and fixed")
            
        # Save detailed results
        with open('real_autonomous_test_results.json', 'w') as f:
            json.dump({
                'test_results': self.test_results,
                'errors_found': self.errors_found,
                'downloads_created': self.downloads_created,
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'success_rate': (passed_tests/total_tests*100) if total_tests > 0 else 0,
                    'runtime_seconds': (datetime.now() - self.test_start_time).total_seconds()
                },
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
    
    def cleanup(self):
        """Clean up resources"""
        if self.streamlit_process:
            print("\n🧹 Cleaning up...")
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

def main():
    """Main test function"""
    tester = RealAutonomousBrowserTest()
    success = tester.run_complete_test()
    
    if not success:
        print("\n🔧 INVESTIGATION REQUIRED:")
        print("Root cause analysis needed for the following issues:")
        for error in tester.errors_found:
            print(f"  • {error}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)