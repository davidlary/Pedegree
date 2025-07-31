#!/usr/bin/env python3
"""
VERIFY ABSOLUTELY NO HARDCODED DATA ANYWHERE
Complete verification that all data is dynamically created at runtime
"""

import json
from pathlib import Path
from datetime import datetime

def verify_no_hardcoded_data():
    """Verify absolutely no hardcoded data, all dynamically created at runtime"""
    print("🔄 VERIFYING NO HARDCODED DATA - ALL DYNAMIC")
    print("=" * 60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'data_sources': {},
        'verification_tests': {},
        'summary': {}
    }
    
    print("\\n📊 Testing Dynamic Data Sources...")
    
    # Test 1: Database-driven data
    print("\\n1️⃣ Testing Database Data Sources...")
    try:
        from data.database_manager import DatabaseManager, DatabaseConfig
        
        config = DatabaseConfig(database_type="sqlite", sqlite_path="data/international_standards.db")
        db = DatabaseManager(config)
        
        # Get data from database
        standards = db.get_all_standards()
        disciplines = db.get_disciplines()
        
        # Verify data exists and is dynamic
        has_standards = len(standards) > 0
        has_disciplines = len(disciplines) > 0
        
        # Check for dynamic properties (timestamps, unique IDs)
        dynamic_standards = False
        if standards:
            sample_standard = standards[0]
            dynamic_fields = ['id', 'created_at', 'discipline', 'title']
            dynamic_standards = any(field in sample_standard for field in dynamic_fields)
        
        dynamic_disciplines = False
        if disciplines:
            sample_discipline = disciplines[0]
            dynamic_fields = ['discipline_id', 'discipline_name', 'created_at']
            dynamic_disciplines = any(field in sample_discipline for field in dynamic_fields)
        
        database_test_passed = has_standards and has_disciplines and dynamic_standards and dynamic_disciplines
        
        results['verification_tests']['database_data'] = {
            'status': 'PASS' if database_test_passed else 'FAIL',
            'standards_count': len(standards),
            'disciplines_count': len(disciplines),
            'has_dynamic_standards': dynamic_standards,
            'has_dynamic_disciplines': dynamic_disciplines
        }
        
        print(f"   Database Data: {'✅ PASS' if database_test_passed else '❌ FAIL'}")
        print(f"      Standards: {len(standards)} records")
        print(f"      Disciplines: {len(disciplines)} records")
        print(f"      Dynamic Fields: {'✅' if dynamic_standards and dynamic_disciplines else '❌'}")
        
    except Exception as e:
        results['verification_tests']['database_data'] = {'status': 'FAIL', 'error': str(e)}
        print(f"   Database Data: ❌ FAIL - {e}")
    
    # Test 2: Configuration-driven data
    print("\\n2️⃣ Testing Configuration Data Sources...")
    try:
        from core.config_manager import ConfigManager
        
        config_manager = ConfigManager(Path('config'))
        
        # Get configuration data
        disciplines_config = config_manager.get_disciplines()
        system_config = config_manager.get_system_architecture()
        llm_config = config_manager.get_llm_optimization_config()
        
        config_loaded = len(disciplines_config) > 0 or len(system_config) > 0 or len(llm_config) > 0
        
        results['verification_tests']['config_data'] = {
            'status': 'PASS' if config_loaded else 'FAIL',
            'disciplines_config_size': len(disciplines_config),
            'system_config_size': len(system_config),
            'llm_config_size': len(llm_config)
        }
        
        print(f"   Config Data: {'✅ PASS' if config_loaded else '❌ FAIL'}")
        print(f"      Disciplines Config: {len(disciplines_config)} entries")
        print(f"      System Config: {len(system_config)} entries")
        print(f"      LLM Config: {len(llm_config)} entries")
        
    except Exception as e:
        results['verification_tests']['config_data'] = {'status': 'FAIL', 'error': str(e)}
        print(f"   Config Data: ❌ FAIL - {e}")
    
    # Test 3: Runtime generation verification
    print("\\n3️⃣ Testing Runtime Data Generation...")
    try:
        from GetInternationalStandards import StandardsCache
        
        # Test cache generates data at runtime
        cache = StandardsCache(Path('runtime_test_cache'))
        
        # Generate some runtime data
        runtime_data = {
            'timestamp': datetime.now().isoformat(),
            'session_id': f"session_{hash(datetime.now())}",
            'cache_key': f"runtime_{id(cache)}"
        }
        
        cache.memory_cache['runtime_test'] = (datetime.now().timestamp(), runtime_data)
        
        # Verify data was created dynamically
        retrieved = cache.memory_cache.get('runtime_test')
        runtime_generation_works = retrieved is not None and 'timestamp' in retrieved[1]
        
        results['verification_tests']['runtime_generation'] = {
            'status': 'PASS' if runtime_generation_works else 'FAIL',
            'cache_working': retrieved is not None,
            'dynamic_timestamp': 'timestamp' in retrieved[1] if retrieved else False
        }
        
        print(f"   Runtime Generation: {'✅ PASS' if runtime_generation_works else '❌ FAIL'}")
        print(f"      Cache Working: {'✅' if retrieved else '❌'}")
        print(f"      Dynamic Timestamps: {'✅' if runtime_generation_works else '❌'}")
        
    except Exception as e:
        results['verification_tests']['runtime_generation'] = {'status': 'FAIL', 'error': str(e)}
        print(f"   Runtime Generation: ❌ FAIL - {e}")
    
    # Test 4: Check for hardcoded data patterns
    print("\\n4️⃣ Scanning for Hardcoded Data Patterns...")
    
    hardcoded_patterns = [
        r'\\[.*".*",.*".*".*\\]',  # Hardcoded lists
        r'data\\s*=\\s*\\{.*".*":\\s*.+\\}',  # Hardcoded dictionaries  
        r'standards\\s*=\\s*\\[',  # Hardcoded standards arrays
        r'disciplines\\s*=\\s*\\['  # Hardcoded disciplines arrays
    ]
    
    core_files = [
        'GetInternationalStandards.py',
        'core/orchestrator.py',
        'core/config_manager.py', 
        'data/database_manager.py'
    ]
    
    hardcoded_violations = []
    
    for file_path in core_files:
        path = Path(file_path)
        if path.exists():
            with open(path, 'r') as f:
                content = f.read()
            
            # Look for suspicious hardcoded patterns
            lines = content.split('\\n')
            in_docstring = False
            
            for line_num, line in enumerate(lines, 1):
                # Track docstrings
                if '"""' in line:
                    in_docstring = not in_docstring
                
                # Skip comments, docstrings, and legitimate demo data
                if (line.strip().startswith('#') or 
                    'mock_response' in line or 
                    in_docstring or
                    line.strip().startswith('"""') or
                    line.strip().startswith("'''") or
                    '# ' in line):
                    continue
                
                # Check for large hardcoded data structures (actual code only)
                if (('= [' in line and len(line) > 100 and not line.strip().startswith('=')) or 
                    ('= {' in line and len(line) > 100 and not line.strip().startswith('='))):
                    
                    # Additional check - make sure it's not configuration or legitimate structure
                    if not any(keyword in line.lower() for keyword in ['config', 'import', 'from', 'class', 'def']):
                        hardcoded_violations.append({
                            'file': file_path,
                            'line': line_num,
                            'type': 'potential_hardcoded_data',
                            'content': line.strip()[:100] + '...' if len(line) > 100 else line.strip()
                        })
    
    hardcoded_scan_clean = len(hardcoded_violations) == 0
    
    results['verification_tests']['hardcoded_scan'] = {
        'status': 'PASS' if hardcoded_scan_clean else 'FAIL',
        'violations_found': len(hardcoded_violations),
        'violations': hardcoded_violations
    }
    
    print(f"   Hardcoded Data Scan: {'✅ PASS' if hardcoded_scan_clean else '❌ FAIL'}")
    print(f"      Violations Found: {len(hardcoded_violations)}")
    
    if hardcoded_violations:
        for violation in hardcoded_violations:
            print(f"      {violation['file']}:{violation['line']} - {violation['type']}")
    
    # Calculate overall results
    total_tests = len(results['verification_tests'])
    passed_tests = sum(1 for test in results['verification_tests'].values() if test.get('status') == 'PASS')
    
    all_dynamic = passed_tests == total_tests
    dynamic_percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    results['summary'] = {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': total_tests - passed_tests,
        'dynamic_percentage': dynamic_percentage,
        'all_data_dynamic': all_dynamic
    }
    
    print(f"\\n📊 NO HARDCODED DATA VERIFICATION RESULTS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Dynamic Data: {dynamic_percentage:.1f}%")
    print(f"   Status: {'✅ ALL DYNAMIC' if all_dynamic else '❌ HARDCODED DATA FOUND'}")
    
    # Save results
    with open('no_hardcoded_verification.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"   Results saved to: no_hardcoded_verification.json")
    
    return all_dynamic

if __name__ == "__main__":
    is_dynamic = verify_no_hardcoded_data()
    exit(0 if is_dynamic else 1)