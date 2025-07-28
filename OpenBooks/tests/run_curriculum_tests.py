#!/usr/bin/env python3
"""
Test Runner for Master Curriculum Builder System

Goal: Comprehensive test execution and reporting for the master curriculum builder
to ensure all components work correctly and maintain high code quality.

This script runs all tests and provides detailed reporting on:
1. Test coverage and results
2. Performance metrics
3. Error detection and validation
4. Integration test results
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_tests():
    """
    Goal: Execute all master curriculum builder tests with comprehensive reporting.
    
    Runs unit tests, integration tests, and generates coverage reports.
    """
    print("🧪 Running Master Curriculum Builder Test Suite")
    print("=" * 60)
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Test files to run
    test_files = [
        "tests/test_master_curriculum_builder.py",
        "tests/test_curricula_integration.py"
    ]
    
    # Check if test files exist
    missing_files = []
    for test_file in test_files:
        if not Path(test_file).exists():
            missing_files.append(test_file)
    
    if missing_files:
        print(f"❌ Missing test files: {', '.join(missing_files)}")
        return False
    
    # Run tests
    all_passed = True
    start_time = time.time()
    
    for test_file in test_files:
        print(f"\n🔍 Running {test_file}...")
        print("-" * 40)
        
        try:
            # Run pytest with verbose output
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file, 
                "-v", 
                "--tb=short",
                "--durations=10"
            ], capture_output=True, text=True, timeout=300)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            if result.returncode != 0:
                print(f"❌ {test_file} FAILED")
                all_passed = False
            else:
                print(f"✅ {test_file} PASSED")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file} TIMED OUT")
            all_passed = False
        except Exception as e:
            print(f"💥 {test_file} ERROR: {e}")
            all_passed = False
    
    # Run all tests together for coverage
    print(f"\n📊 Running complete test suite...")
    print("-" * 40)
    
    try:
        # Run all tests together
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/test_master_curriculum_builder.py",
            "tests/test_curricula_integration.py",
            "-v",
            "--tb=short",
            "--durations=10",
            "--strict-markers"
        ], capture_output=True, text=True, timeout=600)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        suite_passed = result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Complete test suite TIMED OUT")
        suite_passed = False
    except Exception as e:
        print(f"💥 Complete test suite ERROR: {e}")
        suite_passed = False
    
    # Generate summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"⏱️  Total Duration: {duration:.2f} seconds")
    print(f"📁 Test Files: {len(test_files)}")
    
    if all_passed and suite_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Master Curriculum Builder system is working correctly")
        print("✅ Integration with main curricula system is functional") 
        print("✅ All educational sequencing logic is validated")
        print("✅ Visual artifact generation is working")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        print("\n⚠️  Please review test output above for specific failures")
        print("⚠️  Fix issues before deploying curriculum system")
        return False


def check_dependencies():
    """
    Goal: Verify all required dependencies are available for testing.
    
    Checks for pytest, required modules, and test environment setup.
    """
    print("🔧 Checking Test Dependencies")
    print("-" * 30)
    
    # Check pytest
    try:
        import pytest
        print(f"✅ pytest {pytest.__version__}")
    except ImportError:
        print("❌ pytest not found - install with: pip install pytest")
        return False
    
    # Check required modules
    required_modules = [
        "pandas",
        "numpy", 
        "matplotlib",
        "networkx",
        "seaborn"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module}")
    
    if missing_modules:
        print(f"\n⚠️  Missing modules: {', '.join(missing_modules)}")
        print("Install with: pip install " + " ".join(missing_modules))
        return False
    
    # Check core modules
    try:
        from core.master_curriculum_builder import MasterCurriculumBuilder
        print("✅ core.master_curriculum_builder")
    except ImportError as e:
        print(f"❌ core.master_curriculum_builder: {e}")
        return False
    
    print("✅ All dependencies available")
    return True


def main():
    """
    Goal: Main test execution with dependency checking and error handling.
    
    Provides comprehensive test execution with proper setup validation.
    """
    print("🚀 Master Curriculum Builder Test Suite")
    print("Testing comprehensive curriculum generation system")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Dependency check failed - cannot run tests")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    
    # Run tests
    success = run_tests()
    
    if success:
        print("\n🎯 TESTING COMPLETE - ALL SYSTEMS GO!")
        sys.exit(0)
    else:
        print("\n🔥 TESTING FAILED - REVIEW AND FIX ISSUES")
        sys.exit(1)


if __name__ == "__main__":
    main()