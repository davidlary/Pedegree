#!/usr/bin/env python3
"""
Test Streamlit App Startup

This script tests if the Streamlit app can start without errors
by checking imports and basic initialization.
"""

import sys
import subprocess
import time
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_streamlit_startup():
    """Test if Streamlit app can start without errors."""
    print("🧪 Testing Streamlit app startup...")
    
    try:
        # Test syntax and basic imports
        with open('ReadOpenBooks.py', 'r') as f:
            code = f.read()
        
        # Compile to check syntax
        compile(code, 'ReadOpenBooks.py', 'exec')
        print("✅ ReadOpenBooks.py syntax valid")
        
        # Test if app can be imported without execution
        test_code = '''
import sys
from pathlib import Path

# Add current directory to path  
current_dir = Path(__file__).parent if __name__ != "__main__" else Path.cwd()
sys.path.insert(0, str(current_dir))

# Test core imports
from core.config import OpenBooksConfig
from core.terminal_ui import TerminalUI
from core.orchestrator import OpenBooksOrchestrator
from core.enhanced_logging import OperationLogger
from core.data_config import get_data_config
from core.book_discoverer import BookDiscoverer
from core.repository_manager import RepositoryManager
from core.content_processor import ContentProcessor
from core.search_indexer import SearchIndexer

# Test PDF processing imports (optional)
try:
    from core.pdf_integration import PDFContentManager, check_pdf_processing_status
    PDF_PROCESSING_AVAILABLE = True
except ImportError:
    PDF_PROCESSING_AVAILABLE = False

print("✅ All imports successful")

# Test basic initialization
config = OpenBooksConfig()
print("✅ Configuration initialization successful")

print("🎉 Streamlit app ready for execution")
'''
        
        # Run test in subprocess
        result = subprocess.run([
            sys.executable, '-c', test_code
        ], capture_output=True, text=True, timeout=30, cwd=current_dir)
        
        if result.returncode == 0:
            print("✅ Streamlit app imports and initialization successful")
            print(result.stdout)
            return True
        else:
            print(f"❌ Startup test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Startup test timed out")
        return False
    except Exception as e:
        print(f"❌ Startup test error: {e}")
        return False

def test_streamlit_config():
    """Test Streamlit configuration."""
    print("\n🧪 Testing Streamlit configuration...")
    
    try:
        import streamlit as st
        
        # Test basic Streamlit functionality
        print(f"✅ Streamlit version: {st.__version__}")
        
        # Test if we can access key Streamlit functions
        functions_to_test = [
            'markdown', 'write', 'columns', 'tabs', 'selectbox', 
            'button', 'progress', 'spinner', 'success', 'error', 'warning'
        ]
        
        missing_functions = []
        for func_name in functions_to_test:
            if not hasattr(st, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            print(f"❌ Missing Streamlit functions: {missing_functions}")
            return False
        else:
            print("✅ All required Streamlit functions available")
            return True
            
    except Exception as e:
        print(f"❌ Streamlit config test failed: {e}")
        return False

def run_startup_tests():
    """Run all startup tests."""
    print("🚀 ReadOpenBooks Streamlit Startup Test")
    print("=" * 50)
    
    tests = [
        ("Streamlit Configuration", test_streamlit_config),
        ("App Startup", test_streamlit_startup)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Startup Test Results")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} startup tests passed")
    
    if passed == total:
        print("🎉 All startup tests passed!")
        print("\n🚀 ReadOpenBooks is ready to launch!")
        print("Run: streamlit run ReadOpenBooks.py")
        return True
    else:
        print("⚠️ Some startup tests failed")
        return False

if __name__ == "__main__":
    success = run_startup_tests()
    sys.exit(0 if success else 1)