#!/usr/bin/env python3
"""
Test script for ReadOpenBooks installation and functionality.
This script validates that all components are working correctly.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Streamlit: {e}")
        return False
    
    try:
        from core.config import OpenBooksConfig
        from core.data_config import get_data_config
        from core.orchestrator import OpenBooksOrchestrator
        from core.book_discoverer import BookDiscoverer
        from core.repository_manager import RepositoryManager
        from core.content_processor import ContentProcessor
        from core.search_indexer import SearchIndexer
        from core.language_detector import LanguageDetector
        print("✅ All core modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import core modules: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration initialization."""
    print("\n🧪 Testing configuration...")
    
    try:
        from core.config import OpenBooksConfig
        config = OpenBooksConfig()
        print("✅ OpenBooksConfig initialized successfully")
        
        from core.data_config import get_data_config
        data_config = get_data_config()
        languages = data_config.get_supported_languages()
        print(f"✅ Data config loaded, supported languages: {languages}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_core_components():
    """Test core component initialization."""
    print("\n🧪 Testing core components...")
    
    try:
        from core.config import OpenBooksConfig
        from core.book_discoverer import BookDiscoverer
        from core.repository_manager import RepositoryManager
        from core.content_processor import ContentProcessor
        from core.language_detector import LanguageDetector
        
        config = OpenBooksConfig()
        
        # Test BookDiscoverer
        discoverer = BookDiscoverer(config)
        print("✅ BookDiscoverer initialized successfully")
        
        # Test RepositoryManager
        repo_manager = RepositoryManager(config)
        print("✅ RepositoryManager initialized successfully")
        
        # Test ContentProcessor
        content_processor = ContentProcessor(config)
        print("✅ ContentProcessor initialized successfully")
        
        # Test LanguageDetector
        language_detector = LanguageDetector()
        print("✅ LanguageDetector initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ Core components test failed: {e}")
        return False

def test_directory_structure():
    """Test directory structure."""
    print("\n🧪 Testing directory structure...")
    
    directories = {
        "Books": current_dir / "Books",
        "Config": current_dir / "config",
        "Core": current_dir / "core",
        "Tests": current_dir / "tests"
    }
    
    success = True
    for name, path in directories.items():
        if path.exists():
            print(f"✅ {name} directory exists: {path}")
        else:
            print(f"❌ {name} directory missing: {path}")
            success = False
    
    return success

def test_optional_features():
    """Test optional features like PDF processing."""
    print("\n🧪 Testing optional features...")
    
    # Test PDF processing
    try:
        from core.pdf_integration import PDFContentManager, check_pdf_processing_status
        print("✅ PDF processing modules available")
        pdf_available = True
    except ImportError:
        print("⚠️ PDF processing modules not available (optional)")
        pdf_available = False
    
    # Test API keys
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_key:
        print("✅ Anthropic API key configured")
    else:
        print("⚠️ Anthropic API key not configured (optional for PDF processing)")
    
    return True  # Optional features don't fail the test

def test_streamlit_application():
    """Test ReadOpenBooks.py application structure."""
    print("\n🧪 Testing Streamlit application...")
    
    app_file = current_dir / "ReadOpenBooks.py"
    if app_file.exists():
        print("✅ ReadOpenBooks.py exists")
        
        # Test basic syntax by importing
        try:
            # Read the file content to check for syntax errors
            with open(app_file, 'r') as f:
                content = f.read()
            
            # Try to compile it
            compile(content, str(app_file), 'exec')
            print("✅ ReadOpenBooks.py syntax is valid")
            
            return True
        except SyntaxError as e:
            print(f"❌ ReadOpenBooks.py has syntax errors: {e}")
            return False
        except Exception as e:
            print(f"⚠️ ReadOpenBooks.py warning: {e}")
            return True
    else:
        print("❌ ReadOpenBooks.py not found")
        return False

def run_all_tests():
    """Run all tests and report results."""
    print("🚀 Running ReadOpenBooks Installation Tests")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Core Components", test_core_components),
        ("Directory Structure", test_directory_structure),
        ("Optional Features", test_optional_features),
        ("Streamlit Application", test_streamlit_application)
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
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ReadOpenBooks is ready to use.")
        print("\nTo start the application, run:")
        print("streamlit run ReadOpenBooks.py")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)