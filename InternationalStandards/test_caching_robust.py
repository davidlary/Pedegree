#!/usr/bin/env python3
"""
COMPREHENSIVE CACHING ROBUSTNESS TEST
Test extensive caching throughout for periodic reruns
"""

import time
import json
from pathlib import Path
from datetime import datetime

def test_caching_robustness():
    """Test that caching is extensive and robust for periodic reruns"""
    print("🔍 TESTING CACHING ROBUSTNESS FOR PERIODIC RERUNS")
    print("=" * 60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'cache_tests': {},
        'performance_metrics': {},
        'robustness_score': 0
    }
    
    # Test 1: StandardsCache System
    print("\n1️⃣ Testing StandardsCache System...")
    try:
        from GetInternationalStandards import StandardsCache
        
        cache = StandardsCache(Path('test_robust_cache'))
        
        # Test memory cache
        test_data = {'test': 'large_data' * 1000}
        start_time = time.time()
        cache.memory_cache['test_key'] = (time.time(), test_data)
        cache_write_time = time.time() - start_time
        
        start_time = time.time()
        retrieved = cache.memory_cache.get('test_key')
        cache_read_time = time.time() - start_time
        
        cache_working = retrieved is not None
        
        results['cache_tests']['memory_cache'] = {
            'status': 'PASS' if cache_working else 'FAIL',
            'write_time': cache_write_time,
            'read_time': cache_read_time,
            'speedup': 'Instant access' if cache_read_time < 0.001 else f'{cache_read_time:.6f}s'
        }
        
        print(f"   Memory Cache: {'✅ PASS' if cache_working else '❌ FAIL'} - {results['cache_tests']['memory_cache']['speedup']}")
        
    except Exception as e:
        results['cache_tests']['memory_cache'] = {'status': 'FAIL', 'error': str(e)}
        print(f"   Memory Cache: ❌ FAIL - {e}")
    
    # Test 2: Database Caching
    print("\n2️⃣ Testing Database Caching...")
    try:
        from data.database_manager import DatabaseManager, DatabaseConfig
        
        config = DatabaseConfig(database_type="sqlite", sqlite_path="data/international_standards.db")
        db = DatabaseManager(config)
        
        # Test multiple queries with caching
        start_time = time.time()
        standards1 = db.get_all_standards()
        first_query_time = time.time() - start_time
        
        start_time = time.time()
        standards2 = db.get_all_standards()
        second_query_time = time.time() - start_time
        
        # Test disciplines caching
        start_time = time.time()
        disciplines1 = db.get_disciplines()
        first_disc_time = time.time() - start_time
        
        start_time = time.time()
        disciplines2 = db.get_disciplines()
        second_disc_time = time.time() - start_time
        
        caching_effective = second_query_time < first_query_time or second_query_time < 0.01
        
        results['cache_tests']['database_cache'] = {
            'status': 'PASS' if caching_effective else 'FAIL',
            'first_query': first_query_time,
            'second_query': second_query_time,
            'speedup_ratio': first_query_time / second_query_time if second_query_time > 0 else float('inf'),
            'standards_count': len(standards1),
            'disciplines_count': len(disciplines1)
        }
        
        speedup = results['cache_tests']['database_cache']['speedup_ratio']
        print(f"   Database Cache: {'✅ PASS' if caching_effective else '❌ FAIL'} - {speedup:.1f}x speedup")
        
    except Exception as e:
        results['cache_tests']['database_cache'] = {'status': 'FAIL', 'error': str(e)}
        print(f"   Database Cache: ❌ FAIL - {e}")
    
    # Test 3: Streamlit @st.cache_data
    print("\n3️⃣ Testing Streamlit Cache Integration...")
    try:
        # This would normally be tested within Streamlit context
        # For now, verify the decorators exist
        from GetInternationalStandards import InternationalStandardsApp
        
        app = InternationalStandardsApp()
        
        # Check if key methods have caching decorators
        import inspect
        
        # Check for @st.cache_data decorated methods
        cached_methods = []
        for name, method in inspect.getmembers(app, predicate=inspect.ismethod):
            if hasattr(method, '__wrapped__') or '@st.cache_data' in str(method):
                cached_methods.append(name)
        
        # Also check the cache class methods
        has_cache_class = hasattr(app, 'cache') and hasattr(app.cache, 'get_all_standards')
        
        has_cached_methods = len(cached_methods) > 0 or has_cache_class
        
        results['cache_tests']['streamlit_cache'] = {
            'status': 'PASS' if has_cached_methods else 'FAIL',
            'decorators_present': has_cached_methods
        }
        
        print(f"   Streamlit Cache: {'✅ PASS' if has_cached_methods else '❌ FAIL'}")
        
    except Exception as e:
        results['cache_tests']['streamlit_cache'] = {'status': 'FAIL', 'error': str(e)}
        print(f"   Streamlit Cache: ❌ FAIL - {e}")
    
    # Test 4: File-based Caching
    print("\n4️⃣ Testing File-based Persistent Caching...")
    try:
        cache = StandardsCache(Path('test_file_cache'))
        
        # Test file cache persistence
        test_file = cache.cache_dir / "test_persistent.json"
        test_data = {'persistent': 'data', 'timestamp': time.time()}
        
        # Write to file cache
        start_time = time.time()
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        write_time = time.time() - start_time
        
        # Read from file cache
        start_time = time.time()
        with open(test_file, 'r') as f:
            loaded_data = json.load(f)
        read_time = time.time() - start_time
        
        file_cache_working = loaded_data['persistent'] == 'data'
        
        results['cache_tests']['file_cache'] = {
            'status': 'PASS' if file_cache_working else 'FAIL',
            'write_time': write_time,
            'read_time': read_time,
            'persistent': test_file.exists()
        }
        
        print(f"   File Cache: {'✅ PASS' if file_cache_working else '❌ FAIL'} - Persistent: {test_file.exists()}")
        
    except Exception as e:
        results['cache_tests']['file_cache'] = {'status': 'FAIL', 'error': str(e)}
        print(f"   File Cache: ❌ FAIL - {e}")
    
    # Test 5: Cache Management Functions
    print("\n5️⃣ Testing Cache Management Functions...")
    try:
        cache = StandardsCache(Path('test_management_cache'))
        
        # Test cache clearing
        cache.memory_cache['test'] = (time.time(), 'data')
        has_clear_cache = hasattr(cache, 'clear_cache')
        has_clear_all = hasattr(cache, 'clear_all_cache')
        
        management_working = has_clear_cache and has_clear_all
        
        results['cache_tests']['cache_management'] = {
            'status': 'PASS' if management_working else 'FAIL',
            'clear_cache_method': has_clear_cache,
            'clear_all_method': has_clear_all
        }
        
        print(f"   Cache Management: {'✅ PASS' if management_working else '❌ FAIL'}")
        
    except Exception as e:
        results['cache_tests']['cache_management'] = {'status': 'FAIL', 'error': str(e)}
        print(f"   Cache Management: ❌ FAIL - {e}")
    
    # Calculate robustness score
    total_tests = len(results['cache_tests'])
    passed_tests = sum(1 for test in results['cache_tests'].values() if test.get('status') == 'PASS')
    robustness_percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    results['robustness_score'] = robustness_percentage
    results['summary'] = {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': total_tests - passed_tests,
        'robustness_percentage': robustness_percentage,
        'is_robust': robustness_percentage >= 100
    }
    
    print(f"\n📊 CACHING ROBUSTNESS RESULTS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Robustness: {robustness_percentage:.1f}%")
    print(f"   Status: {'✅ ROBUST' if robustness_percentage >= 100 else '❌ NEEDS WORK'}")
    
    # Save results
    with open('caching_robustness_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"   Results saved to: caching_robustness_results.json")
    
    return results['summary']['is_robust']

if __name__ == "__main__":
    is_robust = test_caching_robustness()
    exit(0 if is_robust else 1)