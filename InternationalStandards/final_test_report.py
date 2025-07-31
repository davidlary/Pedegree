#!/usr/bin/env python3
"""
Final Comprehensive Test Report Generator
Combines all test results and provides complete pass/fail status for every component
"""

import json
import sys
from pathlib import Path
from datetime import datetime

class FinalTestReportGenerator:
    def __init__(self):
        self.final_report = {
            'report_timestamp': datetime.now().isoformat(),
            'test_categories': {
                'component_tests': {},
                'ui_tests': {},
                'integration_tests': {}
            },
            'summary': {
                'total_test_categories': 0,
                'passed_categories': 0,
                'failed_categories': 0,
                'total_individual_tests': 0,
                'passed_individual_tests': 0,
                'failed_individual_tests': 0,
                'overall_success_rate': 0.0
            },
            'detailed_results': {},
            'recommendations': []
        }
    
    def load_component_test_results(self):
        """Load component test results"""
        try:
            with open('test_results_comprehensive.json', 'r') as f:
                component_results = json.load(f)
            
            self.final_report['test_categories']['component_tests'] = component_results
            
            # Update summary
            summary = component_results['summary']
            self.final_report['summary']['total_individual_tests'] += summary['total_tests']
            self.final_report['summary']['passed_individual_tests'] += summary['passed_tests']  
            self.final_report['summary']['failed_individual_tests'] += summary['failed_tests']
            
            # Component category assessment
            if summary['passed_components'] >= summary['total_components'] * 0.8:
                self.final_report['summary']['passed_categories'] += 1
            else:
                self.final_report['summary']['failed_categories'] += 1
            
            self.final_report['summary']['total_test_categories'] += 1
            
            print("✅ Component test results loaded")
            return True
            
        except FileNotFoundError:
            print("❌ Component test results not found")
            return False
    
    def load_ui_test_results(self):
        """Load UI test results"""
        try:
            with open('streamlit_ui_test_results.json', 'r') as f:
                ui_results = json.load(f)
            
            self.final_report['test_categories']['ui_tests'] = ui_results
            
            # Update summary
            summary = ui_results['summary']
            ui_total_tests = summary['passed_tests'] + summary['failed_tests']
            self.final_report['summary']['total_individual_tests'] += ui_total_tests
            self.final_report['summary']['passed_individual_tests'] += summary['passed_tests']
            self.final_report['summary']['failed_individual_tests'] += summary['failed_tests']
            
            # UI category assessment
            ui_success_rate = (summary['passed_tests'] / ui_total_tests * 100) if ui_total_tests > 0 else 0
            if ui_success_rate >= 80:
                self.final_report['summary']['passed_categories'] += 1
            else:
                self.final_report['summary']['failed_categories'] += 1
                
            self.final_report['summary']['total_test_categories'] += 1
            
            print("✅ UI test results loaded")
            return True
            
        except FileNotFoundError:
            print("❌ UI test results not found") 
            return False
    
    def run_final_integration_test(self):
        """Run final integration test"""
        print("🔍 Running final integration test...")
        
        integration_results = {
            'test_timestamp': datetime.now().isoformat(),
            'tests': [],
            'passed': 0,
            'failed': 0
        }
        
        # Test 1: End-to-end Streamlit startup
        try:
            import subprocess
            import time
            
            process = subprocess.Popen([
                sys.executable, '-m', 'streamlit', 'run',
                'GetInternationalStandards.py',
                '--server.headless', 'true',
                '--server.port', '8506'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            time.sleep(8)
            
            if process.poll() is None:
                integration_results['tests'].append({
                    'test_name': 'End_to_End_Streamlit_Startup',
                    'status': 'PASS',
                    'details': 'Application starts successfully end-to-end'
                })
                integration_results['passed'] += 1
                
                # Clean shutdown
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            else:
                stdout, stderr = process.communicate()
                integration_results['tests'].append({
                    'test_name': 'End_to_End_Streamlit_Startup', 
                    'status': 'FAIL',
                    'error': f'Application failed to start: {stderr[:200]}'
                })
                integration_results['failed'] += 1
                
        except Exception as e:
            integration_results['tests'].append({
                'test_name': 'End_to_End_Streamlit_Startup',
                'status': 'FAIL', 
                'error': str(e)
            })
            integration_results['failed'] += 1
        
        # Test 2: All core modules importable together
        try:
            from GetInternationalStandards import InternationalStandardsApp
            from core.orchestrator import StandardsOrchestrator
            from core.llm_integration import LLMIntegration
            from data.database_manager import DatabaseManager
            from quality.quality_scoring import QualityScoringEngine
            from api.api_generator import APIGenerator
            
            integration_results['tests'].append({
                'test_name': 'All_Core_Modules_Import',
                'status': 'PASS',
                'details': 'All core modules can be imported together without conflicts'
            })
            integration_results['passed'] += 1
            
        except Exception as e:
            integration_results['tests'].append({
                'test_name': 'All_Core_Modules_Import',
                'status': 'FAIL',
                'error': str(e)
            })
            integration_results['failed'] += 1
        
        # Test 3: Configuration integrity
        try:
            config_files = [
                'config/openalex_disciplines.yaml',
                'config/standards_ecosystem.yaml', 
                'config/recovery_system.yaml',
                'config/llm_optimization.yaml',
                'config/system_architecture.yaml'
            ]
            
            all_configs_valid = True
            for config_file in config_files:
                if not Path(config_file).exists() or Path(config_file).stat().st_size == 0:
                    all_configs_valid = False
                    break
            
            if all_configs_valid:
                integration_results['tests'].append({
                    'test_name': 'Configuration_Integrity',
                    'status': 'PASS',
                    'details': 'All configuration files present and non-empty'
                })
                integration_results['passed'] += 1
            else:
                integration_results['tests'].append({
                    'test_name': 'Configuration_Integrity',
                    'status': 'FAIL',
                    'error': 'One or more configuration files missing or empty'
                })
                integration_results['failed'] += 1
                
        except Exception as e:
            integration_results['tests'].append({
                'test_name': 'Configuration_Integrity',
                'status': 'FAIL',
                'error': str(e)
            })
            integration_results['failed'] += 1
        
        # Store integration results
        self.final_report['test_categories']['integration_tests'] = integration_results
        
        # Update summary
        total_integration_tests = integration_results['passed'] + integration_results['failed']
        self.final_report['summary']['total_individual_tests'] += total_integration_tests
        self.final_report['summary']['passed_individual_tests'] += integration_results['passed']
        self.final_report['summary']['failed_individual_tests'] += integration_results['failed']
        
        # Integration category assessment
        integration_success_rate = (integration_results['passed'] / total_integration_tests * 100) if total_integration_tests > 0 else 0
        if integration_success_rate >= 80:
            self.final_report['summary']['passed_categories'] += 1
        else:
            self.final_report['summary']['failed_categories'] += 1
            
        self.final_report['summary']['total_test_categories'] += 1
        
        print(f"✅ Integration testing completed: {integration_results['passed']}/{total_integration_tests} passed")
    
    def generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check component test issues
        if 'component_tests' in self.final_report['test_categories']:
            component_results = self.final_report['test_categories']['component_tests']
            
            for component_name, component_data in component_results.get('components_tested', {}).items():
                if component_data['status'] == 'FAIL':
                    failed_tests = [t for t in component_data['tests'] if t['status'] == 'FAIL']
                    for failed_test in failed_tests:
                        recommendations.append({
                            'category': 'component',
                            'component': component_name,
                            'issue': failed_test['test_name'],
                            'recommendation': f"Fix {component_name} {failed_test['test_name']}: {failed_test.get('error', 'Unknown error')}"
                        })
        
        # Check UI test issues  
        if 'ui_tests' in self.final_report['test_categories']:
            ui_results = self.final_report['test_categories']['ui_tests']
            
            for page_name, page_data in ui_results.get('page_tests', {}).items():
                if page_data['status'] == 'FAIL':
                    failed_tests = [t for t in page_data['tests'] if t['status'] == 'FAIL']
                    for failed_test in failed_tests:
                        recommendations.append({
                            'category': 'ui',
                            'page': page_name,
                            'issue': failed_test['test_name'],
                            'recommendation': f"Fix {page_name} {failed_test['test_name']}: {failed_test.get('error', 'Unknown error')}"
                        })
        
        # General recommendations
        overall_success_rate = self.final_report['summary']['overall_success_rate']
        
        if overall_success_rate < 95:
            recommendations.append({
                'category': 'general',
                'recommendation': f'Overall success rate is {overall_success_rate:.1f}%. Consider addressing failed tests to reach >95% target.'
            })
        
        if overall_success_rate >= 90:
            recommendations.append({
                'category': 'deployment',
                'recommendation': 'System is ready for production deployment with minor fixes needed.'
            })
        elif overall_success_rate >= 80:
            recommendations.append({
                'category': 'deployment', 
                'recommendation': 'System is functional but needs moderate improvements before production.'
            })
        else:
            recommendations.append({
                'category': 'deployment',
                'recommendation': 'System needs significant improvements before production deployment.'
            })
        
        self.final_report['recommendations'] = recommendations
    
    def calculate_final_metrics(self):
        """Calculate final success metrics"""
        summary = self.final_report['summary']
        
        if summary['total_individual_tests'] > 0:
            summary['overall_success_rate'] = (summary['passed_individual_tests'] / summary['total_individual_tests']) * 100
        else:
            summary['overall_success_rate'] = 0.0
    
    def print_final_report(self):
        """Print comprehensive final test report"""
        print("\n" + "=" * 100)
        print("🎯 FINAL COMPREHENSIVE TEST REPORT - INTERNATIONAL STANDARDS RETRIEVAL SYSTEM")
        print("=" * 100)
        
        summary = self.final_report['summary']
        
        print(f"📊 EXECUTIVE SUMMARY:")
        print(f"   Report Generated: {self.final_report['report_timestamp']}")
        print(f"   Total Test Categories: {summary['total_test_categories']}")
        print(f"   ✅ Categories Passed: {summary['passed_categories']}")
        print(f"   ❌ Categories Failed: {summary['failed_categories']}")
        print(f"   📈 Category Success Rate: {(summary['passed_categories'] / summary['total_test_categories'] * 100):.1f}%")
        print()
        
        print(f"🔍 DETAILED TEST STATISTICS:")
        print(f"   Total Individual Tests: {summary['total_individual_tests']}")
        print(f"   ✅ Individual Tests Passed: {summary['passed_individual_tests']}")
        print(f"   ❌ Individual Tests Failed: {summary['failed_individual_tests']}")
        print(f"   📈 Overall Success Rate: {summary['overall_success_rate']:.1f}%")
        print()
        
        # Component test results
        if 'component_tests' in self.final_report['test_categories']:
            comp_results = self.final_report['test_categories']['component_tests']
            comp_summary = comp_results.get('summary', {})
            print(f"🔧 COMPONENT TESTING RESULTS:")
            print(f"   Components Tested: {comp_summary.get('total_components', 0)}")
            print(f"   Component Success Rate: {(comp_summary.get('passed_components', 0) / comp_summary.get('total_components', 1) * 100):.1f}%")
            
            # List component results
            for comp_name, comp_data in comp_results.get('components_tested', {}).items():
                status_icon = "✅" if comp_data['status'] == 'PASS' else "❌" 
                print(f"      {status_icon} {comp_name}: {comp_data['passed']}/{comp_data['passed'] + comp_data['failed']} tests")
            print()
        
        # UI test results
        if 'ui_tests' in self.final_report['test_categories']:
            ui_results = self.final_report['test_categories']['ui_tests']
            ui_summary = ui_results.get('summary', {})
            ui_total = ui_summary.get('passed_tests', 0) + ui_summary.get('failed_tests', 0)
            ui_success = (ui_summary.get('passed_tests', 0) / ui_total * 100) if ui_total > 0 else 0
            
            print(f"🖥️  USER INTERFACE TESTING RESULTS:")
            print(f"   Pages Tested: {ui_summary.get('total_pages', 0)}")
            print(f"   Buttons Tested: {ui_summary.get('total_buttons', 0)}")
            print(f"   UI Success Rate: {ui_success:.1f}%")
            
            # List page results
            for page_name, page_data in ui_results.get('page_tests', {}).items():
                status_icon = "✅" if page_data['status'] == 'PASS' else "❌"
                button_count = len(page_data.get('buttons_found', []))
                print(f"      {status_icon} {page_name}: {len(page_data['tests'])} tests, {button_count} buttons")
            print()
        
        # Integration test results
        if 'integration_tests' in self.final_report['test_categories']:
            int_results = self.final_report['test_categories']['integration_tests']
            int_total = int_results.get('passed', 0) + int_results.get('failed', 0)
            int_success = (int_results.get('passed', 0) / int_total * 100) if int_total > 0 else 0
            
            print(f"🔗 INTEGRATION TESTING RESULTS:")
            print(f"   Integration Tests: {int_total}")
            print(f"   Integration Success Rate: {int_success:.1f}%")
            
            for test in int_results.get('tests', []):
                status_icon = "✅" if test['status'] == 'PASS' else "❌"
                print(f"      {status_icon} {test['test_name']}")
            print()
        
        # Recommendations
        if self.final_report['recommendations']:
            print(f"💡 RECOMMENDATIONS:")
            for i, rec in enumerate(self.final_report['recommendations'][:10], 1):  # Top 10
                print(f"   {i}. {rec['recommendation']}")
            print()
        
        # Final assessment
        overall_rate = summary['overall_success_rate']
        print("🎯 FINAL SYSTEM ASSESSMENT:")
        
        if overall_rate >= 95:
            print("   🎉 STATUS: EXCELLENT - System fully ready for production")
            print("   ✅ All major components functional")
            print("   ✅ Minor issues only, system operational")
        elif overall_rate >= 90:
            print("   ✨ STATUS: VERY GOOD - System ready with minor improvements")
            print("   ✅ Core functionality verified")
            print("   ⚠️  Some minor issues to address")
        elif overall_rate >= 80:
            print("   👍 STATUS: GOOD - System functional with moderate issues")
            print("   ✅ Basic functionality working")
            print("   ⚠️  Several issues need attention")
        elif overall_rate >= 70:
            print("   ⚠️  STATUS: ACCEPTABLE - System needs significant work")
            print("   ⚠️  Major functionality issues detected")
            print("   🔧 Substantial debugging required")
        else:
            print("   🚨 STATUS: CRITICAL - System needs major repairs")
            print("   ❌ Multiple critical issues detected")
            print("   🛠️  Extensive debugging required")
        
        print("\n" + "=" * 100)
        print("📄 DETAILED RESULTS SAVED TO: final_comprehensive_test_report.json")
        print("🚀 COMMAND TO RUN SYSTEM: streamlit run GetInternationalStandards.py")
        print("=" * 100)
    
    def save_final_report(self):
        """Save final comprehensive report"""
        try:
            with open('final_comprehensive_test_report.json', 'w') as f:
                json.dump(self.final_report, f, indent=2)
            return True
        except Exception as e:
            print(f"⚠️  Could not save final report: {e}")
            return False
    
    def generate_final_report(self):
        """Generate complete final test report"""
        print("🚀 GENERATING FINAL COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        # Load all test results
        component_loaded = self.load_component_test_results()
        ui_loaded = self.load_ui_test_results()
        
        # Run final integration test
        self.run_final_integration_test()
        
        # Calculate final metrics
        self.calculate_final_metrics()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Print comprehensive report
        self.print_final_report()
        
        # Save report
        self.save_final_report()
        
        return self.final_report['summary']['overall_success_rate'] >= 80

def main():
    """Main execution"""
    generator = FinalTestReportGenerator()
    success = generator.generate_final_report()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)