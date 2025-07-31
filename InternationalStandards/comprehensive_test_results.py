#!/usr/bin/env python3
"""
COMPREHENSIVE TEST RESULTS - SHOW ALL PASS/FAIL STATUS
Complete summary of all testing results
"""

import json
from pathlib import Path
from datetime import datetime

def generate_comprehensive_test_results():
    """Generate comprehensive test results showing pass/fail for every component"""
    print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
    print("=" * 80)
    
    # Load all test result files
    test_files = [
        ('real_test_results.json', 'Core System Tests'),
        ('page_button_test_results.json', 'UI Testing Results'),
        ('caching_robustness_results.json', 'Caching System Tests'),
        ('original_prompt_verification.json', 'Original Prompt Verification'),
        ('no_placeholders_verification.json', 'No Placeholder Verification'),
        ('no_hardcoded_verification.json', 'No Hardcoded Data Verification')
    ]
    
    comprehensive_results = {
        'timestamp': datetime.now().isoformat(),
        'test_categories': {},
        'overall_summary': {}
    }
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    
    for file_path, category_name in test_files:
        print(f"\\n🔍 {category_name}")
        print("-" * 60)
        
        if Path(file_path).exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                category_results = {
                    'category': category_name,
                    'file': file_path,
                    'tests': {},
                    'summary': {}
                }
                
                # Process different result formats
                if 'tests' in data:
                    # real_test_results.json format
                    for test_name, test_result in data['tests'].items():
                        status = test_result.get('status', 'UNKNOWN')
                        details = test_result.get('details', 'No details')
                        
                        category_results['tests'][test_name] = {
                            'status': status,
                            'details': details
                        }
                        
                        print(f"  {'✅' if status == 'PASS' else '❌'} {test_name.replace('_', ' ').title()}: {status}")
                        print(f"     {details}")
                        
                        total_tests += 1
                        if status == 'PASS':
                            total_passed += 1
                        else:
                            total_failed += 1
                
                elif 'pages_tested' in data or 'buttons_tested' in data:
                    # page_button_test_results.json format
                    if 'pages_tested' in data:
                        for page_name, page_result in data['pages_tested'].items():
                            status = page_result.get('status', 'UNKNOWN')
                            category_results['tests'][f'page_{page_name}'] = {
                                'status': status,
                                'details': page_result.get('details', '')
                            }
                            
                            print(f"  {'✅' if status == 'PASS' else '❌'} Page {page_name}: {status}")
                            
                            total_tests += 1
                            if status == 'PASS':
                                total_passed += 1
                            else:
                                total_failed += 1
                    
                    if 'buttons_tested' in data:
                        for button_name, button_result in data['buttons_tested'].items():
                            status = button_result.get('status', 'UNKNOWN')
                            category_results['tests'][f'button_{button_name}'] = {
                                'status': status,
                                'details': button_result.get('details', '')
                            }
                            
                            print(f"  {'✅' if status == 'PASS' else '❌'} Button {button_name}: {status}")
                            
                            total_tests += 1
                            if status == 'PASS':
                                total_passed += 1
                            else:
                                total_failed += 1
                
                elif 'cache_tests' in data:
                    # caching_robustness_results.json format
                    for test_name, test_result in data['cache_tests'].items():
                        status = test_result.get('status', 'UNKNOWN')
                        details = test_result.get('details', 'No details')
                        
                        category_results['tests'][test_name] = {
                            'status': status,
                            'details': details
                        }
                        
                        print(f"  {'✅' if status == 'PASS' else '❌'} {test_name.replace('_', ' ').title()}: {status}")
                        print(f"     {details}")
                        
                        total_tests += 1
                        if status == 'PASS':
                            total_passed += 1
                        else:
                            total_failed += 1
                
                elif 'original_aspects' in data:
                    # original_prompt_verification.json format
                    for aspect_name, aspect_result in data['original_aspects'].items():
                        impl_status = aspect_result.get('implementation_status', 'UNKNOWN')
                        test_status = aspect_result.get('testing_status', 'UNKNOWN')
                        
                        # Count as pass if both implemented and tested
                        overall_status = 'PASS' if impl_status == 'IMPLEMENTED' and test_status == 'TESTED' else 'FAIL'
                        
                        category_results['tests'][aspect_name] = {
                            'status': overall_status,
                            'details': f"Implementation: {impl_status}, Testing: {test_status}"
                        }
                        
                        print(f"  {'✅' if overall_status == 'PASS' else '❌'} {aspect_name.replace('_', ' ').title()}: {overall_status}")
                        print(f"     {aspect_result.get('description', '')}")
                        
                        total_tests += 1
                        if overall_status == 'PASS':
                            total_passed += 1
                        else:
                            total_failed += 1
                
                elif 'verification_tests' in data:
                    # verification result format
                    for test_name, test_result in data['verification_tests'].items():
                        status = test_result.get('status', 'UNKNOWN')
                        details = test_result.get('details', 'No details')
                        
                        category_results['tests'][test_name] = {
                            'status': status,
                            'details': details
                        }
                        
                        print(f"  {'✅' if status == 'PASS' else '❌'} {test_name.replace('_', ' ').title()}: {status}")
                        if 'error' not in test_result:
                            print(f"     {details}")
                        
                        total_tests += 1
                        if status == 'PASS':
                            total_passed += 1
                        else:
                            total_failed += 1
                
                elif 'placeholder_scan' in data:
                    # no_placeholders_verification.json format
                    core_files = data['placeholder_scan']['core_files']
                    test_files_data = data['placeholder_scan']['test_files']
                    
                    category_results['tests']['core_files_clean'] = {
                        'status': 'PASS' if core_files['violations'] == 0 else 'FAIL',
                        'details': f"{core_files['clean']}/{core_files['total']} core files clean"
                    }
                    
                    category_results['tests']['test_files_clean'] = {
                        'status': 'PASS' if test_files_data['violations'] == 0 else 'FAIL',
                        'details': f"{test_files_data['clean']}/{test_files_data['total']} test files clean"
                    }
                    
                    print(f"  {'✅' if core_files['violations'] == 0 else '❌'} Core Files Clean: {'PASS' if core_files['violations'] == 0 else 'FAIL'}")
                    print(f"     {core_files['clean']}/{core_files['total']} files passed ({core_files['clean_percentage']:.1f}%)")
                    
                    print(f"  {'✅' if test_files_data['violations'] == 0 else '❌'} Test Files Clean: {'PASS' if test_files_data['violations'] == 0 else 'FAIL'}")
                    print(f"     {test_files_data['clean']}/{test_files_data['total']} files passed ({test_files_data['clean_percentage']:.1f}%)")
                    
                    total_tests += 2
                    if core_files['violations'] == 0:
                        total_passed += 1
                    else:
                        total_failed += 1
                        
                    if test_files_data['violations'] == 0:
                        total_passed += 1
                    else:
                        total_failed += 1
                
                # Add category summary
                category_tests = len(category_results['tests'])
                category_passed = sum(1 for test in category_results['tests'].values() if test['status'] == 'PASS')
                category_results['summary'] = {
                    'total_tests': category_tests,
                    'passed_tests': category_passed,
                    'failed_tests': category_tests - category_passed,
                    'success_rate': (category_passed / category_tests * 100) if category_tests > 0 else 0
                }
                
                print(f"\\n  📊 Category Summary: {category_passed}/{category_tests} passed ({category_results['summary']['success_rate']:.1f}%)")
                
                comprehensive_results['test_categories'][category_name] = category_results
                
            except Exception as e:
                print(f"  ❌ Error loading {file_path}: {e}")
                comprehensive_results['test_categories'][category_name] = {
                    'error': str(e),
                    'file': file_path
                }
        else:
            print(f"  ⚠️ File not found: {file_path}")
            comprehensive_results['test_categories'][category_name] = {
                'error': 'File not found',
                'file': file_path
            }
    
    # Calculate overall results
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    comprehensive_results['overall_summary'] = {
        'total_tests': total_tests,
        'total_passed': total_passed,
        'total_failed': total_failed,
        'success_rate': success_rate,
        'status': 'PASS' if success_rate >= 95 else 'NEEDS_ATTENTION'
    }
    
    print(f"\\n{'=' * 80}")
    print(f"🏆 OVERALL TEST RESULTS SUMMARY")
    print(f"{'=' * 80}")
    print(f"📊 Total Tests Run: {total_tests}")
    print(f"✅ Tests Passed: {total_passed}")
    print(f"❌ Tests Failed: {total_failed}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print(f"🎯 Overall Status: {comprehensive_results['overall_summary']['status']}")
    
    # Save comprehensive results
    with open('comprehensive_test_results.json', 'w') as f:
        json.dump(comprehensive_results, f, indent=2)
    
    print(f"\\n💾 Results saved to: comprehensive_test_results.json")
    
    return comprehensive_results['overall_summary']['status'] == 'PASS'

if __name__ == "__main__":
    success = generate_comprehensive_test_results()
    exit(0 if success else 1)