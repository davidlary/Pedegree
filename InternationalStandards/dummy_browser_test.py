#!/usr/bin/env python3
"""
AUTONOMOUS DUMMY BROWSER TEST - Comprehensive end-to-end testing
Tests the entire system like a user would, including actual standards processing
"""

import subprocess
import time
import requests
import threading
import json
from pathlib import Path

class DummyBrowserTest:
    def __init__(self):
        self.streamlit_process = None
        self.base_url = "http://localhost:8502"
        self.app_instance = None
        
    def start_streamlit_server(self):
        """Start the Streamlit server"""
        print("🚀 Starting Streamlit server...")
        
        # Start streamlit in background
        self.streamlit_process = subprocess.Popen(
            ["streamlit", "run", "GetInternationalStandards.py", "--server.port=8502"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get(self.base_url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ Streamlit server started at {self.base_url}")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
            print(f"  Waiting for server... ({i+1}/30)")
        
        print("❌ Failed to start Streamlit server")
        return False
    
    def stop_streamlit_server(self):
        """Stop the Streamlit server"""
        if self.streamlit_process:
            print("🛑 Stopping Streamlit server...")
            self.streamlit_process.terminate()
            self.streamlit_process.wait()
            self.streamlit_process = None
    
    def get_app_instance(self):
        """Get direct access to the app instance for testing"""
        try:
            from GetInternationalStandards import InternationalStandardsApp
            self.app_instance = InternationalStandardsApp()
            return self.app_instance is not None
        except Exception as e:
            print(f"❌ Failed to get app instance: {e}")
            return False
    
    def test_home_page(self):
        """Test that home page loads"""
        print("\n📄 Testing Home Page...")
        try:
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                print("✅ Home page loads successfully")
                return True
            else:
                print(f"❌ Home page failed with status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Home page test failed: {e}")
            return False
    
    def simulate_start_system_click(self):
        """Simulate clicking 'Start System' and verify agents actually start"""
        print("\n🎯 Simulating 'Start System' click...")
        
        if not self.app_instance:
            if not self.get_app_instance():
                return False
        
        try:
            # Test all disciplines like the UI does
            all_disciplines = [
                "Physical_Sciences", "Life_Sciences", "Health_Sciences", "Social_Sciences",
                "Computer_Science", "Mathematics", "Engineering", "Business", "Economics",
                "Geography", "Environmental_Science", "Earth_Sciences", "Agricultural_Sciences",
                "History", "Philosophy", "Art", "Literature", "Education", "Law"
            ]
            
            print(f"  Starting system with {len(all_disciplines)} disciplines...")
            
            # Start the system
            if self.app_instance.orchestrator:
                result = self.app_instance.orchestrator.start_system(all_disciplines)
                print(f"  System start result: {result}")
                
                if result:
                    # Wait for initialization
                    print("  Waiting for agents to initialize...")
                    time.sleep(5)
                    
                    # Check system status
                    status = self.app_instance.orchestrator.get_system_status()
                    is_running = status.get('is_running', False)
                    system_metrics = status.get('system_metrics', {})
                    active_agents = system_metrics.get('total_agents_active', 0)
                    
                    print(f"  System running: {is_running}")
                    print(f"  Active agents: {active_agents}")
                    
                    if is_running and active_agents > 0:
                        print("✅ Start System successful - agents are active")
                        return True, active_agents
                    else:
                        print("❌ Start System failed - agents not active")
                        return False, 0
                else:
                    print("❌ System start failed")
                    return False, 0
            else:
                print("❌ No orchestrator available")
                return False, 0
                
        except Exception as e:
            print(f"❌ Start System simulation failed: {e}")
            import traceback
            traceback.print_exc()
            return False, 0
    
    def verify_agents_processing_standards(self, timeout=60):
        """Verify agents are actually processing standards, not just idle"""
        print("\n🔍 Verifying agents are processing standards...")
        
        if not self.app_instance or not self.app_instance.orchestrator:
            print("❌ No app instance or orchestrator available")
            return False
        
        try:
            # Create some discovery tasks to trigger processing
            disciplines_to_test = ["Physical_Sciences", "Computer_Science", "Mathematics"]
            
            print(f"  Creating discovery tasks for {len(disciplines_to_test)} disciplines...")
            
            task_ids = []
            for discipline in disciplines_to_test:
                task_id = self.app_instance.orchestrator.add_task(
                    task_type="discovery",
                    discipline=discipline,
                    parameters={
                        "search_terms": ["educational standards", "curriculum standards"],
                        "max_results": 5,
                        "test_mode": True  # Indicate this is a test
                    },
                    priority=1  # High priority
                )
                task_ids.append(task_id)
                print(f"    Added task {task_id} for {discipline}")
            
            # Wait and monitor for actual processing
            start_time = time.time()
            processing_detected = False
            completed_tasks = 0
            
            while time.time() - start_time < timeout:
                status = self.app_instance.orchestrator.get_system_status()
                
                # Check for running agents
                agents = status.get('agents', {})
                running_agents = [aid for aid, agent in agents.items() if agent.get('status') == 'running']
                
                # Check task progress
                tasks = status.get('tasks', {})
                in_progress_tasks = tasks.get('in_progress', 0)
                completed_tasks = tasks.get('completed', 0)
                
                if running_agents:
                    processing_detected = True
                    print(f"  ✅ PROCESSING DETECTED: {len(running_agents)} agents running")
                    print(f"     Running agents: {running_agents[:3]}...")  # Show first 3
                
                if in_progress_tasks > 0:
                    print(f"  ✅ TASKS IN PROGRESS: {in_progress_tasks} tasks")
                
                if completed_tasks > 0:
                    print(f"  ✅ COMPLETED TASKS: {completed_tasks} tasks")
                
                # Check if we have evidence of actual processing
                if processing_detected and (in_progress_tasks > 0 or completed_tasks > 0):
                    print("  🎉 SUCCESS: Agents are actively processing standards!")
                    
                    # Get detailed agent status
                    agent_details = self.app_instance.orchestrator.get_agent_status()
                    active_agents = [(aid, details) for aid, details in agent_details.items() 
                                   if details.get('status') in ['running', 'idle']]
                    
                    print(f"  📊 Agent Summary:")
                    print(f"     Total active agents: {len(active_agents)}")
                    print(f"     Tasks in progress: {in_progress_tasks}")
                    print(f"     Tasks completed: {completed_tasks}")
                    
                    # Show some processing examples
                    for i, (agent_id, details) in enumerate(active_agents[:5]):
                        status_str = details.get('status', 'unknown')
                        task_count = details.get('standards_found', 0)
                        success_rate = details.get('success_rate', 0.0)
                        print(f"     Agent {i+1}: {status_str} | Found: {task_count} | Success: {success_rate:.1%}")
                    
                    return True
                
                time.sleep(2)
                print(f"  Monitoring... ({int(time.time() - start_time)}s elapsed)")
            
            print(f"❌ Timeout: No active processing detected in {timeout} seconds")
            print(f"   Processing detected: {processing_detected}")
            print(f"   Completed tasks: {completed_tasks}")
            return False
            
        except Exception as e:
            print(f"❌ Standards processing verification failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_dashboard_functionality(self):
        """Test that dashboard shows real data"""
        print("\n📊 Testing Dashboard functionality...")
        
        if not self.app_instance:
            return False
        
        try:
            # Get system status
            status = self.app_instance.orchestrator.get_system_status()
            agent_details = self.app_instance.orchestrator.get_agent_status()
            
            print(f"  System metrics available: {bool(status.get('system_metrics'))}")
            print(f"  Agent details available: {len(agent_details)} agents")
            print(f"  Discipline progress available: {bool(status.get('discipline_progress'))}")
            
            # Check for actual data
            system_metrics = status.get('system_metrics', {})
            active_agents = system_metrics.get('total_agents_active', 0)
            
            if active_agents > 0:
                print("✅ Dashboard has real agent data")
                return True
            else:
                print("❌ Dashboard shows no active agents")
                return False
            
        except Exception as e:
            print(f"❌ Dashboard test failed: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete end-to-end test"""
        print("🎯 AUTONOMOUS DUMMY BROWSER TEST - COMPREHENSIVE END-TO-END")
        print("=" * 70)
        
        test_results = {}
        
        try:
            # Step 1: Start Streamlit server
            if not self.start_streamlit_server():
                test_results['server_start'] = False
                return test_results
            test_results['server_start'] = True
            
            # Step 2: Test home page
            test_results['home_page'] = self.test_home_page()
            
            # Step 3: Get app instance for direct testing
            test_results['app_instance'] = self.get_app_instance()
            
            # Step 4: Simulate Start System click
            start_success, agent_count = self.simulate_start_system_click()
            test_results['start_system'] = start_success
            test_results['agent_count'] = agent_count
            
            if start_success:
                # Step 5: Verify agents are actually processing standards
                test_results['standards_processing'] = self.verify_agents_processing_standards()
                
                # Step 6: Test dashboard functionality
                test_results['dashboard'] = self.test_dashboard_functionality()
            else:
                test_results['standards_processing'] = False
                test_results['dashboard'] = False
            
            return test_results
            
        except Exception as e:
            print(f"❌ Comprehensive test failed: {e}")
            import traceback
            traceback.print_exc()
            test_results['error'] = str(e)
            return test_results
            
        finally:
            # Always cleanup
            self.stop_streamlit_server()
    
    def print_test_summary(self, results):
        """Print a summary of test results"""
        print("\n" + "=" * 70)
        print("🎯 AUTONOMOUS TEST RESULTS SUMMARY")
        print("=" * 70)
        
        total_tests = len([k for k in results.keys() if k != 'error'])
        passed_tests = len([k for k, v in results.items() if v is True])
        
        print(f"📊 Overall: {passed_tests}/{total_tests} tests passed")
        print()
        
        test_descriptions = {
            'server_start': 'Streamlit server startup',
            'home_page': 'Home page loading', 
            'app_instance': 'App instance creation',
            'start_system': 'Start System functionality',
            'standards_processing': 'CRITICAL: Agents processing standards',
            'dashboard': 'Dashboard functionality'
        }
        
        for test_key, description in test_descriptions.items():
            if test_key in results:
                status = "✅ PASS" if results[test_key] else "❌ FAIL"
                if test_key == 'standards_processing':
                    status = status + " (CRITICAL TEST)"
                print(f"{status}: {description}")
        
        if 'agent_count' in results:
            print(f"📈 Agent Count: {results['agent_count']} agents active")
        
        if 'error' in results:
            print(f"❌ Error: {results['error']}")
        
        # Final verdict
        print("\n" + "=" * 70)
        if results.get('standards_processing', False):
            print("🎉 OVERALL RESULT: SUCCESS - Agents are actively processing standards!")
            print("   The system is working end-to-end as expected.")
        else:
            print("❌ OVERALL RESULT: FAILED - Agents are NOT processing standards")
            print("   The system needs debugging and fixes.")
        print("=" * 70)
        
        return results.get('standards_processing', False)

def main():
    """Main test execution"""
    tester = DummyBrowserTest()
    results = tester.run_comprehensive_test()
    success = tester.print_test_summary(results)
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)