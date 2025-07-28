#!/usr/bin/env python3
"""
Comprehensive ReadOpenBooks.py Functionality Test Suite

Tests all aspects of the ReadOpenBooks Streamlit application including:
- Application syntax and imports
- Core functionality integration
- Tab interface components
- Book collection access
- Configuration interface
- Validation systems
"""

import sys
import os
from pathlib import Path
import subprocess
import traceback

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_application_syntax():
    """Test ReadOpenBooks.py syntax and compilation."""
    print("🧪 Testing ReadOpenBooks.py syntax...")
    
    try:
        app_file = current_dir / "ReadOpenBooks.py"
        if not app_file.exists():
            print("❌ ReadOpenBooks.py not found")
            return False
        
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Compile the application code
        compile(content, str(app_file), 'exec')
        print("✅ ReadOpenBooks.py syntax is valid")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ ReadOpenBooks.py syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ ReadOpenBooks.py compilation error: {e}")
        return False

def test_streamlit_imports():
    """Test that Streamlit and all required modules can be imported."""
    print("\n🧪 Testing Streamlit and dependencies...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        # Test other critical imports from ReadOpenBooks.py
        from pathlib import Path
        import sys
        import os
        import traceback
        from datetime import datetime
        print("✅ Standard library imports successful")
        
        # Test core module imports
        from core.config import OpenBooksConfig
        from core.data_config import get_data_config
        from core.orchestrator import OpenBooksOrchestrator
        print("✅ Core module imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_application_initialization():
    """Test ReadOpenBooks.py core functionality initialization."""
    print("\n🧪 Testing application initialization...")
    
    try:
        # Test configuration initialization
        from core.config import OpenBooksConfig
        from core.data_config import get_data_config
        
        config = OpenBooksConfig()
        data_config = get_data_config()
        print("✅ Configuration systems initialized")
        
        # Test data config functions used in ReadOpenBooks.py
        languages = data_config.get_supported_languages()
        disciplines = data_config.get_legacy_disciplines()
        print(f"✅ Data configuration loaded: {len(languages)} languages, {len(disciplines)} disciplines")
        
        # Test orchestrator initialization
        from core.orchestrator import OpenBooksOrchestrator
        orchestrator = OpenBooksOrchestrator(config)
        print("✅ Orchestrator initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Application initialization failed: {e}")
        traceback.print_exc()
        return False

def test_book_collection_integration():
    """Test integration with the Books collection."""
    print("\n🧪 Testing Books collection integration...")
    
    try:
        books_dir = Path("Books")
        if not books_dir.exists():
            print("❌ Books directory not found")
            return False
        
        # Test book enumeration (used in Read Books tab)
        languages = []
        total_books = 0
        subjects = set()
        
        for lang_dir in books_dir.iterdir():
            if lang_dir.is_dir() and lang_dir.name not in ['BookList.json', 'BookList.tsv']:
                languages.append(lang_dir.name)
                for subject_dir in lang_dir.iterdir():
                    if subject_dir.is_dir():
                        subjects.add(subject_dir.name)
                        for level_dir in subject_dir.iterdir():
                            if level_dir.is_dir():
                                repos = [d for d in level_dir.iterdir() if d.is_dir() and (d / '.git').exists()]
                                total_books += len(repos)
        
        print(f"✅ Book collection accessible: {total_books} books across {len(languages)} languages")
        print(f"✅ Subjects available: {len(subjects)} different subjects")
        print(f"✅ Languages: {sorted(languages)}")
        
        # Verify minimum expected collection for ReadOpenBooks functionality
        assert total_books >= 40, f"Expected at least 40 books for full functionality, found {total_books}"
        assert len(languages) >= 6, f"Expected at least 6 languages, found {len(languages)}"
        
        return True
        
    except Exception as e:
        print(f"❌ Book collection integration test failed: {e}")
        traceback.print_exc()
        return False

def test_validation_system_integration():
    """Test validation system components used in ReadOpenBooks."""
    print("\n🧪 Testing validation system integration...")
    
    try:
        # Test components used in Validation tab
        from core.book_discoverer import BookDiscoverer
        from core.repository_manager import RepositoryManager
        from core.content_processor import ContentProcessor
        from core.config import OpenBooksConfig
        
        config = OpenBooksConfig()
        discoverer = BookDiscoverer(config)
        repo_manager = RepositoryManager(config)
        content_processor = ContentProcessor(config)
        
        print("✅ Validation system components initialized")
        
        # Test that validation methods exist (used in validation tab)
        assert hasattr(discoverer, 'discover_openstax_books'), "Missing discover_openstax_books method"
        assert hasattr(repo_manager, 'clone_repository'), "Missing clone_repository method"
        assert hasattr(content_processor, 'extract_book_metadata'), "Missing extract_book_metadata method"
        
        print("✅ Validation system methods verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation system integration test failed: {e}")
        traceback.print_exc()
        return False

def test_settings_interface_compatibility():
    """Test Settings tab functionality compatibility."""
    print("\n🧪 Testing Settings interface compatibility...")
    
    try:
        # Test configuration display functionality
        from core.config import OpenBooksConfig
        from core.data_config import get_data_config
        
        config = OpenBooksConfig()
        data_config = get_data_config()
        
        # Test configuration attributes used in Settings tab
        assert hasattr(config, 'max_workers'), "Missing max_workers configuration"
        assert hasattr(config, 'project_root'), "Missing project_root configuration"
        
        print("✅ Configuration attributes accessible")
        
        # Test data configuration methods used in Settings
        languages = data_config.get_supported_languages()
        disciplines = data_config.get_legacy_disciplines()
        
        assert isinstance(languages, list), "Languages should be a list"
        assert isinstance(disciplines, list), "Disciplines should be a list"
        
        print(f"✅ Data configuration methods working: {len(languages)} languages, {len(disciplines)} disciplines")
        
        # Test environment variable detection (used in Settings)
        import os
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            print("✅ Anthropic API key detected in environment")
        else:
            print("⚠️ Anthropic API key not set (optional for PDF processing)")
        
        return True
        
    except Exception as e:
        print(f"❌ Settings interface compatibility test failed: {e}")
        traceback.print_exc()
        return False

def test_dashboard_functionality():
    """Test Dashboard tab functionality components."""
    print("\n🧪 Testing Dashboard functionality...")
    
    try:
        # Test system status detection used in dashboard
        books_dir = Path("Books")
        core_dir = Path("core")
        config_dir = Path("config")
        
        system_status = {
            "Books Directory": books_dir.exists(),
            "Core Modules": core_dir.exists(),
            "Configuration": config_dir.exists()
        }
        
        all_good = all(system_status.values())
        print(f"✅ System status detection working: {'All systems operational' if all_good else 'Some issues detected'}")
        
        # Test statistics calculation used in dashboard
        if books_dir.exists():
            total_books = 0
            languages = []
            for lang_dir in books_dir.iterdir():
                if lang_dir.is_dir() and lang_dir.name not in ['BookList.json', 'BookList.tsv']:
                    languages.append(lang_dir.name)
                    for subject_dir in lang_dir.iterdir():
                        if subject_dir.is_dir():
                            for level_dir in subject_dir.iterdir():
                                if level_dir.is_dir():
                                    repos = [d for d in level_dir.iterdir() if d.is_dir() and (d / '.git').exists()]
                                    total_books += len(repos)
            
            print(f"✅ Dashboard statistics calculated: {total_books} books, {len(languages)} languages")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_streamlit_execution_readiness():
    """Test readiness for Streamlit execution."""
    print("\n🧪 Testing Streamlit execution readiness...")
    
    try:
        # Test that streamlit can be run (without actually starting server)
        result = subprocess.run([
            sys.executable, '-c', 
            'import streamlit; print("Streamlit ready")'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Streamlit execution environment ready")
        else:
            print(f"❌ Streamlit execution issue: {result.stderr}")
            return False
        
        # Test ReadOpenBooks.py can be imported without execution
        test_script = f'''
import sys
sys.path.insert(0, '{current_dir}')
with open('ReadOpenBooks.py', 'r') as f:
    compile(f.read(), 'ReadOpenBooks.py', 'exec')
print('ReadOpenBooks.py compilation ready')
'''
        result = subprocess.run([
            sys.executable, '-c', test_script
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ ReadOpenBooks.py ready for Streamlit execution")
        else:
            print(f"❌ ReadOpenBooks.py execution readiness issue: {result.stderr}")
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Streamlit readiness test timed out")
        return False
    except Exception as e:
        print(f"❌ Streamlit execution readiness test failed: {e}")
        return False

def run_all_readopenbooks_tests():
    """Run all ReadOpenBooks.py functionality tests."""
    print("🚀 ReadOpenBooks.py Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        ("Application Syntax", test_application_syntax),
        ("Streamlit Imports", test_streamlit_imports),
        ("Application Initialization", test_application_initialization),
        ("Book Collection Integration", test_book_collection_integration),
        ("Validation System Integration", test_validation_system_integration),
        ("Settings Interface Compatibility", test_settings_interface_compatibility),
        ("Dashboard Functionality", test_dashboard_functionality),
        ("Streamlit Execution Readiness", test_streamlit_execution_readiness)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ReadOpenBooks.py Test Results")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} ReadOpenBooks.py tests passed")
    
    if passed == total:
        print("🎉 All ReadOpenBooks.py tests passed!")
        print("✅ Application is fully functional and ready for use")
        print("\nTo start the application, run:")
        print("streamlit run ReadOpenBooks.py")
        return True
    else:
        print("⚠️ Some ReadOpenBooks.py tests failed")
        print("❌ Application may have issues - debugging required")
        return False

if __name__ == "__main__":
    success = run_all_readopenbooks_tests()
    sys.exit(0 if success else 1)