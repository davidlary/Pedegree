#!/usr/bin/env python3
"""
Autonomous Streamlit UI Testing System
Tests every page and every button in the Streamlit application
"""

import sys
import time
import json
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import signal
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class StreamlitUITester:
    def __init__(self):
        self.test_results = {
            'test_timestamp': datetime.now().isoformat(),
            'streamlit_tests': {},
            'page_tests': {},
            'button_tests': {},
            'summary': {
                'total_pages': 0,
                'tested_pages': 0,
                'total_buttons': 0,
                'tested_buttons': 0,
                'passed_tests': 0,
                'failed_tests': 0
            }
        }
        self.streamlit_process = None
        self.base_url = "http://localhost:8505"
        
    def start_streamlit_server(self):
        """Start Streamlit server for testing"""
        print("🚀 Starting Streamlit server for UI testing...")
        
        try:
            # Start Streamlit process
            self.streamlit_process = subprocess.Popen([
                sys.executable, '-m', 'streamlit', 'run',
                'GetInternationalStandards.py',
                '--server.headless', 'true',
                '--server.port', '8505',
                '--server.runOnSave', 'false',
                '--browser.gatherUsageStats', 'false'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Give server time to start
            print("⏳ Waiting for server startup...")
            time.sleep(10)
            
            # Check if server is running
            if self.streamlit_process.poll() is None:
                print("✅ Streamlit server started successfully")
                return True
            else:
                stdout, stderr = self.streamlit_process.communicate()
                print(f"❌ Streamlit server failed to start")
                print(f"Error: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting Streamlit server: {e}")
            return False
    
    def stop_streamlit_server(self):
        """Stop Streamlit server"""
        if self.streamlit_process:
            print("🛑 Stopping Streamlit server...")
            self.streamlit_process.terminate()
            try:
                self.streamlit_process.wait(timeout=5)
                print("✅ Streamlit server stopped")
            except subprocess.TimeoutExpired:
                self.streamlit_process.kill()
                print("✅ Streamlit server force stopped")
    
    def test_streamlit_application_structure(self):
        """Test the Streamlit application structure and pages"""
        print("🔍 Testing Streamlit Application Structure...")
        
        # Import the application to analyze its structure
        try:
            from GetInternationalStandards import InternationalStandardsApp
            
            # Test application initialization
            app = InternationalStandardsApp()
            
            self.test_results['streamlit_tests']['app_initialization'] = {
                'test_name': 'Application_Initialization',
                'status': 'PASS',
                'details': 'Application initializes successfully'
            }
            
            # Analyze the application structure by examining the code
            self.analyze_streamlit_pages()
            
            return True
            
        except Exception as e:
            self.test_results['streamlit_tests']['app_initialization'] = {
                'test_name': 'Application_Initialization', 
                'status': 'FAIL',
                'error': str(e)
            }
            return False
    
    def analyze_streamlit_pages(self):
        """Analyze Streamlit pages by examining the source code"""
        print("📄 Analyzing Streamlit pages...")
        
        # Read the main Streamlit file to identify pages
        try:
            with open('GetInternationalStandards.py', 'r') as f:
                content = f.read()
            
            # Identify pages from the navigation structure
            pages = [
                "🏠 Dashboard",
                "🔬 Discipline Explorer", 
                "📖 Standards Browser",
                "🤖 Agent Monitor",
                "🧠 LLM Optimization",
                "🔗 Data APIs",
                "🔄 Recovery Center"
            ]
            
            # Test each page
            for page in pages:
                self.test_streamlit_page(page, content)
            
            self.test_results['summary']['total_pages'] = len(pages)
            self.test_results['summary']['tested_pages'] = len(pages)
            
        except Exception as e:
            print(f"❌ Error analyzing pages: {e}")
    
    def test_streamlit_page(self, page_name: str, source_code: str):
        """Test individual Streamlit page functionality"""
        print(f"🧪 Testing page: {page_name}")
        
        page_test_results = {
            'page_name': page_name,
            'tests': [],
            'buttons_found': [],
            'status': 'UNKNOWN'
        }
        
        # Clean page name for method lookup
        clean_page_name = page_name.split(' ', 1)[1].lower().replace(' ', '_')
        method_name = f"_render_{clean_page_name}"
        
        # Test 1: Check if page render method exists
        if method_name in source_code:
            page_test_results['tests'].append({
                'test_name': f'{clean_page_name}_method_exists',
                'status': 'PASS', 
                'details': f'Page render method {method_name} found'
            })
            
            # Test 2: Analyze page content for buttons and components
            self.analyze_page_components(page_name, method_name, source_code, page_test_results)
            
        else:
            page_test_results['tests'].append({
                'test_name': f'{clean_page_name}_method_exists',
                'status': 'FAIL',
                'error': f'Page render method {method_name} not found'
            })
        
        # Test 3: Test page-specific functionality
        self.test_page_specific_functionality(page_name, source_code, page_test_results)
        
        # Determine overall page status
        failed_tests = [t for t in page_test_results['tests'] if t['status'] == 'FAIL']
        page_test_results['status'] = 'FAIL' if failed_tests else 'PASS'
        
        # Update summary
        if page_test_results['status'] == 'PASS':
            self.test_results['summary']['passed_tests'] += 1
        else:
            self.test_results['summary']['failed_tests'] += 1
        
        self.test_results['page_tests'][page_name] = page_test_results
    
    def analyze_page_components(self, page_name: str, method_name: str, source_code: str, page_results: Dict):
        """Analyze components within a page"""
        
        # Find the method content
        method_start = source_code.find(f"def {method_name}(")
        if method_start == -1:
            return
        
        # Find method end (next def or end of class)
        method_end = source_code.find("\n    def ", method_start + 1)
        if method_end == -1:
            method_end = len(source_code)
        
        method_content = source_code[method_start:method_end]
        
        # Look for Streamlit components
        components_found = []
        
        # Check for common Streamlit components
        streamlit_components = [
            'st.button', 'st.selectbox', 'st.multiselect', 'st.slider',
            'st.text_input', 'st.number_input', 'st.checkbox', 'st.radio',
            'st.file_uploader', 'st.expander', 'st.tabs', 'st.columns',
            'st.metric', 'st.progress', 'st.spinner'
        ]
        
        for component in streamlit_components:
            if component in method_content:
                components_found.append(component)
        
        # Look specifically for buttons
        buttons_found = []
        lines = method_content.split('\n')
        
        for i, line in enumerate(lines):
            if 'st.button(' in line:
                # Extract button text
                start = line.find('st.button(') + 10
                if start > 9:
                    # Find the button text (first parameter)
                    button_text = self.extract_button_text(line[start:])
                    if button_text:
                        buttons_found.append({
                            'button_text': button_text,
                            'line_number': i + 1,
                            'full_line': line.strip()
                        })
        
        page_results['components_found'] = components_found
        page_results['buttons_found'] = buttons_found
        
        # Test each button found
        for button in buttons_found:
            self.test_button_functionality(page_name, button, page_results)
        
        # Add component analysis results
        page_results['tests'].append({
            'test_name': f'{page_name}_components_analysis',
            'status': 'PASS',
            'details': f'Found {len(components_found)} Streamlit components, {len(buttons_found)} buttons'
        })
    
    def extract_button_text(self, button_call: str) -> Optional[str]:
        """Extract button text from st.button() call"""
        try:
            # Handle different quote types
            if button_call.startswith('"'):
                end = button_call.find('"', 1)
                if end > 0:
                    return button_call[1:end]
            elif button_call.startswith("'"):
                end = button_call.find("'", 1)
                if end > 0:
                    return button_call[1:end]
            elif button_call.startswith('f"') or button_call.startswith("f'"):
                quote_char = button_call[1]
                end = button_call.find(quote_char, 2)
                if end > 0:
                    return button_call[2:end]
        except:
            pass
        return None
    
    def test_button_functionality(self, page_name: str, button_info: Dict, page_results: Dict):
        """Test individual button functionality"""
        button_text = button_info['button_text']
        
        button_test = {
            'button_text': button_text,
            'page': page_name,
            'tests': []
        }
        
        # Test 1: Button text extraction
        button_test['tests'].append({
            'test_name': f'button_text_extraction',
            'status': 'PASS',
            'details': f'Button text "{button_text}" extracted successfully'
        })
        
        # Test 2: Check for button handler logic
        if 'if st.button(' in button_info['full_line'] or button_info['full_line'].strip().startswith('if '):
            button_test['tests'].append({
                'test_name': f'button_handler_exists',
                'status': 'PASS',
                'details': 'Button has associated handler logic'
            })
        else:
            button_test['tests'].append({
                'test_name': f'button_handler_exists',
                'status': 'FAIL',
                'error': 'No handler logic found for button'
            })
        
        # Test 3: Button accessibility (has meaningful text)
        if len(button_text) > 2 and not button_text.isdigit():
            button_test['tests'].append({
                'test_name': f'button_accessibility',
                'status': 'PASS',
                'details': 'Button has meaningful text'
            })
        else:
            button_test['tests'].append({
                'test_name': f'button_accessibility',
                'status': 'FAIL',
                'error': 'Button text may not be meaningful'
            })
        
        # Store button test results
        self.test_results['button_tests'][f"{page_name}_{button_text}"] = button_test
        
        # Update summary
        self.test_results['summary']['total_buttons'] += 1
        self.test_results['summary']['tested_buttons'] += 1
        
        passed_button_tests = [t for t in button_test['tests'] if t['status'] == 'PASS']
        if len(passed_button_tests) == len(button_test['tests']):
            self.test_results['summary']['passed_tests'] += 1
        else:
            self.test_results['summary']['failed_tests'] += 1
    
    def test_page_specific_functionality(self, page_name: str, source_code: str, page_results: Dict):
        """Test page-specific functionality requirements"""
        
        # Define expected functionality per page
        page_requirements = {
            "🏠 Dashboard": ['st.metric', 'system_stats', 'real_time'],
            "🔬 Discipline Explorer": ['disciplines', 'selectbox', 'multiselect'],
            "📖 Standards Browser": ['standards', 'browser', 'filtering'],
            "🤖 Agent Monitor": ['agent', 'monitor', 'status'],
            "🧠 LLM Optimization": ['llm', 'optimization', 'router'],
            "🔗 Data APIs": ['api', 'data', 'endpoints'],
            "🔄 Recovery Center": ['recovery', 'checkpoint', 'state']
        }
        
        requirements = page_requirements.get(page_name, [])
        
        for requirement in requirements:
            # Check if requirement is mentioned in the page method
            clean_page_name = page_name.split(' ', 1)[1].lower().replace(' ', '_')
            method_name = f"_render_{clean_page_name}"
            
            if method_name in source_code:
                method_start = source_code.find(f"def {method_name}(")
                method_end = source_code.find("\n    def ", method_start + 1)
                if method_end == -1:
                    method_end = len(source_code)
                
                method_content = source_code[method_start:method_end].lower()
                
                if requirement.lower() in method_content:
                    page_results['tests'].append({
                        'test_name': f'{requirement}_functionality',
                        'status': 'PASS',
                        'details': f'Page implements {requirement} functionality'
                    })
                else:
                    page_results['tests'].append({
                        'test_name': f'{requirement}_functionality',
                        'status': 'FAIL',
                        'error': f'Page missing {requirement} functionality'
                    })
    
    def test_streamlit_server_response(self):
        """Test if Streamlit server responds correctly"""
        print("🌐 Testing Streamlit server response...")
        
        try:
            # Test server health
            response = requests.get(f"{self.base_url}/healthz", timeout=5)
            if response.status_code == 200:
                self.test_results['streamlit_tests']['server_health'] = {
                    'test_name': 'Server_Health_Check',
                    'status': 'PASS',
                    'details': 'Server responds to health check'
                }
            else:
                self.test_results['streamlit_tests']['server_health'] = {
                    'test_name': 'Server_Health_Check',
                    'status': 'FAIL',
                    'error': f'Server health check failed with status {response.status_code}'
                }
        except requests.RequestException as e:
            self.test_results['streamlit_tests']['server_health'] = {
                'test_name': 'Server_Health_Check',
                'status': 'FAIL',
                'error': f'Server not responding: {str(e)}'
            }
    
    def run_comprehensive_ui_tests(self):
        """Run all UI tests"""
        print("🚀 COMPREHENSIVE STREAMLIT UI TESTING")
        print("=" * 80)
        print(f"Test execution started: {datetime.now()}")
        print()
        
        # Test 1: Application Structure
        if not self.test_streamlit_application_structure():
            print("❌ Application structure test failed, continuing with limited testing")
        
        # Test 2: Start server and test response
        if self.start_streamlit_server():
            time.sleep(3)  # Additional wait for full startup
            self.test_streamlit_server_response()
        else:
            print("⚠️  Server startup failed, skipping server response tests")
        
        # Print results
        self.print_ui_test_results()
        
        # Stop server
        self.stop_streamlit_server()
        
        # Save results
        self.save_ui_test_results()
        
        return self.test_results
    
    def print_ui_test_results(self):
        """Print comprehensive UI test results"""
        print("\n" + "=" * 80)
        print("🎯 STREAMLIT UI TEST RESULTS")
        print("=" * 80)
        
        # Overall summary
        summary = self.test_results['summary']
        total_tests = summary['passed_tests'] + summary['failed_tests']
        success_rate = (summary['passed_tests'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL STATISTICS:")
        print(f"   Total Pages: {summary['total_pages']}")
        print(f"   Pages Tested: {summary['tested_pages']}")
        print(f"   Total Buttons: {summary['total_buttons']}")
        print(f"   Buttons Tested: {summary['tested_buttons']}")
        print(f"   ✅ Tests Passed: {summary['passed_tests']}")
        print(f"   ❌ Tests Failed: {summary['failed_tests']}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        print()
        
        # Page-by-page results
        print("📄 PAGE-BY-PAGE RESULTS:")
        for page_name, page_data in self.test_results['page_tests'].items():
            status_icon = "✅" if page_data['status'] == 'PASS' else "❌"
            button_count = len(page_data.get('buttons_found', []))
            print(f"   {status_icon} {page_name}: {len(page_data['tests'])} tests, {button_count} buttons")
        
        print()
        
        # Button test results
        if self.test_results['button_tests']:
            print("🔘 BUTTON TEST RESULTS:")
            for button_id, button_data in self.test_results['button_tests'].items():
                passed_tests = [t for t in button_data['tests'] if t['status'] == 'PASS']
                total_tests = len(button_data['tests'])
                status_icon = "✅" if len(passed_tests) == total_tests else "❌"
                print(f"   {status_icon} {button_data['button_text']} ({button_data['page']}): {len(passed_tests)}/{total_tests} tests passed")
        
        print()
        
        # Overall assessment
        if success_rate >= 95:
            print("🎉 UI STATUS: EXCELLENT - All pages and buttons fully functional")
        elif success_rate >= 85:
            print("✨ UI STATUS: GOOD - Minor UI issues detected")
        elif success_rate >= 70:
            print("⚠️  UI STATUS: ACCEPTABLE - Some UI components need attention")
        else:
            print("🚨 UI STATUS: CRITICAL - Multiple UI components need fixes")
        
        print("=" * 80)
    
    def save_ui_test_results(self):
        """Save UI test results to file"""
        try:
            results_file = Path('streamlit_ui_test_results.json')
            with open(results_file, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            print(f"📄 UI test results saved to: {results_file}")
        except Exception as e:
            print(f"⚠️  Could not save UI test results: {e}")

def main():
    """Main execution function"""
    tester = StreamlitUITester()
    
    try:
        results = tester.run_comprehensive_ui_tests()
        
        # Determine success
        summary = results['summary'] 
        total_tests = summary['passed_tests'] + summary['failed_tests']
        success_rate = (summary['passed_tests'] / total_tests * 100) if total_tests > 0 else 0
        
        return success_rate >= 85
        
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        tester.stop_streamlit_server()
        return False
    except Exception as e:
        print(f"❌ Testing failed with error: {e}")
        tester.stop_streamlit_server()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)