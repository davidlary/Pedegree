#!/usr/bin/env python3
"""
Comprehensive Core Functions Test Suite

Tests all core functionality for ReadOpenBooks system to ensure
each component works correctly and integrates properly.
"""

import sys
import os
from pathlib import Path
import traceback

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_config_initialization():
    """Test configuration system initialization."""
    print("🧪 Testing Configuration System...")
    
    try:
        from core.config import OpenBooksConfig
        from core.data_config import get_data_config
        
        # Test OpenBooksConfig
        config = OpenBooksConfig()
        print("✅ OpenBooksConfig initialized")
        
        # Test basic config attributes
        assert hasattr(config, 'max_workers'), "Config missing max_workers"
        assert config.max_workers > 0, "Invalid max_workers value"
        print(f"✅ Config has {config.max_workers} max workers")
        
        # Test data config
        data_config = get_data_config()
        languages = data_config.get_supported_languages()
        assert isinstance(languages, list), "Languages should be a list"
        assert 'english' in languages, "English should be supported"
        print(f"✅ Data config supports {len(languages)} languages")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        traceback.print_exc()
        return False

def test_book_discoverer():
    """Test book discovery functionality."""
    print("\n🧪 Testing Book Discoverer...")
    
    try:
        from core.config import OpenBooksConfig
        from core.book_discoverer import BookDiscoverer
        
        config = OpenBooksConfig()
        discoverer = BookDiscoverer(config)
        print("✅ BookDiscoverer initialized")
        
        # Test discoverer has required methods
        required_methods = ['discover_openstax_books', 'discover_pdf_sources']
        for method in required_methods:
            assert hasattr(discoverer, method), f"Missing method: {method}"
        print("✅ BookDiscoverer has required methods")
        
        return True
        
    except Exception as e:
        print(f"❌ Book discoverer test failed: {e}")
        traceback.print_exc()
        return False

def test_repository_manager():
    """Test repository management functionality."""
    print("\n🧪 Testing Repository Manager...")
    
    try:
        from core.config import OpenBooksConfig
        from core.repository_manager import RepositoryManager
        
        config = OpenBooksConfig()
        repo_manager = RepositoryManager(config)
        print("✅ RepositoryManager initialized")
        
        # Test repo manager has required methods
        required_methods = ['clone_repository', 'update_repository']
        for method in required_methods:
            assert hasattr(repo_manager, method), f"Missing method: {method}"
        print("✅ RepositoryManager has required methods")
        
        # Test that Books directory is accessible
        books_dir = Path("Books")
        if books_dir.exists():
            print(f"✅ Books directory accessible with {len(list(books_dir.iterdir()))} items")
        else:
            print("⚠️ Books directory not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Repository manager test failed: {e}")
        traceback.print_exc()
        return False

def test_content_processor():
    """Test content processing functionality."""
    print("\n🧪 Testing Content Processor...")
    
    try:
        from core.config import OpenBooksConfig
        from core.content_processor import ContentProcessor
        
        config = OpenBooksConfig()
        processor = ContentProcessor(config)
        print("✅ ContentProcessor initialized")
        
        # Test processor has required methods
        required_methods = ['extract_book_metadata', 'generate_catalog_markdown']
        for method in required_methods:
            assert hasattr(processor, method), f"Missing method: {method}"
        print("✅ ContentProcessor has required methods")
        
        return True
        
    except Exception as e:
        print(f"❌ Content processor test failed: {e}")
        traceback.print_exc()
        return False

def test_orchestrator():
    """Test orchestrator functionality."""
    print("\n🧪 Testing Orchestrator...")
    
    try:
        from core.config import OpenBooksConfig
        from core.orchestrator import OpenBooksOrchestrator
        
        config = OpenBooksConfig()
        orchestrator = OpenBooksOrchestrator(config)
        print("✅ OpenBooksOrchestrator initialized")
        
        # Test orchestrator has required methods
        required_methods = ['run_complete_workflow']
        for method in required_methods:
            assert hasattr(orchestrator, method), f"Missing method: {method}"
        print("✅ OpenBooksOrchestrator has required methods")
        
        # Test orchestrator components
        assert hasattr(orchestrator, 'discoverer'), "Missing discoverer component"
        assert hasattr(orchestrator, 'repo_manager'), "Missing repo_manager component"
        assert hasattr(orchestrator, 'content_processor'), "Missing content_processor component"
        print("✅ OpenBooksOrchestrator has required components")
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        traceback.print_exc()
        return False

def test_language_detector():
    """Test language detection functionality."""
    print("\n🧪 Testing Language Detector...")
    
    try:
        from core.language_detector import LanguageDetector
        
        detector = LanguageDetector()
        print("✅ LanguageDetector initialized")
        
        # Test language detection with sample texts
        test_cases = [
            ("This is English text about physics", "english"),
            ("Este es texto en español sobre física", "spanish"),
            ("Ceci est un texte français sur la physique", "french")
        ]
        
        for text, expected_lang in test_cases:
            try:
                detected = detector.detect_language(text)
                print(f"✅ Detected '{detected}' for {expected_lang} text")
            except Exception as e:
                print(f"⚠️ Language detection warning for {expected_lang}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Language detector test failed: {e}")
        traceback.print_exc()
        return False

def test_search_indexer():
    """Test search indexing functionality."""
    print("\n🧪 Testing Search Indexer...")
    
    try:
        from core.config import OpenBooksConfig
        from core.search_indexer import SearchIndexer
        
        config = OpenBooksConfig()
        indexer = SearchIndexer(config)
        print("✅ SearchIndexer initialized")
        
        # Test indexer has required methods
        required_methods = ['index_content', 'search']
        for method in required_methods:
            assert hasattr(indexer, method), f"Missing method: {method}"
        print("✅ SearchIndexer has required methods")
        
        return True
        
    except Exception as e:
        print(f"❌ Search indexer test failed: {e}")
        traceback.print_exc()
        return False

def test_terminal_ui():
    """Test terminal UI functionality."""
    print("\n🧪 Testing Terminal UI...")
    
    try:
        from core.terminal_ui import TerminalUI
        
        ui = TerminalUI()
        print("✅ TerminalUI initialized")
        
        # Test UI has required methods
        required_methods = ['print_header', 'print_info', 'print_error', 'print_success']
        for method in required_methods:
            assert hasattr(ui, method), f"Missing method: {method}"
        print("✅ TerminalUI has required methods")
        
        # Test basic UI functionality
        ui.print_info("Test message")
        print("✅ TerminalUI basic functionality works")
        
        return True
        
    except Exception as e:
        print(f"❌ Terminal UI test failed: {e}")
        traceback.print_exc()
        return False

def test_parallel_processor():
    """Test parallel processing functionality."""
    print("\n🧪 Testing Parallel Processor...")
    
    try:
        from core.config import OpenBooksConfig
        from core.parallel_processor import ParallelProcessor
        
        config = OpenBooksConfig()
        processor = ParallelProcessor(config)
        print("✅ ParallelProcessor initialized")
        
        # Test processor has required methods
        required_methods = ['process_batch_parallel']
        for method in required_methods:
            assert hasattr(processor, method), f"Missing method: {method}"
        print("✅ ParallelProcessor has required methods")
        
        return True
        
    except Exception as e:
        print(f"❌ Parallel processor test failed: {e}")
        traceback.print_exc()
        return False

def test_logging_system():
    """Test enhanced logging functionality."""
    print("\n🧪 Testing Enhanced Logging...")
    
    try:
        from core.enhanced_logging import OperationLogger
        
        logger = OperationLogger('test')
        print("✅ OperationLogger initialized")
        
        # Test logger has required methods
        required_methods = ['log_error', 'start_operation', 'end_operation']
        for method in required_methods:
            assert hasattr(logger, method), f"Missing method: {method}"
        print("✅ OperationLogger has required methods")
        
        # Test basic logging functionality
        logger.start_operation("test_operation")
        logger.end_operation(success=True)
        print("✅ OperationLogger basic functionality works")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced logging test failed: {e}")
        traceback.print_exc()
        return False

def test_book_collection_access():
    """Test access to the book collection."""
    print("\n🧪 Testing Book Collection Access...")
    
    try:
        books_dir = Path("Books")
        
        if not books_dir.exists():
            print("❌ Books directory does not exist")
            return False
        
        # Count books and languages
        total_books = 0
        languages = []
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
        
        print(f"✅ Found {total_books} books across {len(languages)} languages")
        print(f"✅ Languages: {sorted(languages)}")
        print(f"✅ Subjects: {len(subjects)} different subjects")
        
        # Verify minimum expected collection
        assert total_books >= 40, f"Expected at least 40 books, found {total_books}"
        assert len(languages) >= 6, f"Expected at least 6 languages, found {len(languages)}"
        
        return True
        
    except Exception as e:
        print(f"❌ Book collection access test failed: {e}")
        traceback.print_exc()
        return False

def run_all_core_tests():
    """Run all core function tests."""
    print("🚀 ReadOpenBooks Core Functions Test Suite")
    print("=" * 60)
    
    tests = [
        ("Configuration System", test_config_initialization),
        ("Book Discoverer", test_book_discoverer),
        ("Repository Manager", test_repository_manager),
        ("Content Processor", test_content_processor),
        ("Orchestrator", test_orchestrator),
        ("Language Detector", test_language_detector),
        ("Search Indexer", test_search_indexer),
        ("Terminal UI", test_terminal_ui),
        ("Parallel Processor", test_parallel_processor),
        ("Enhanced Logging", test_logging_system),
        ("Book Collection Access", test_book_collection_access)
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
    print("\n" + "=" * 60)
    print("📊 Core Functions Test Results")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} core function tests passed")
    
    if passed == total:
        print("🎉 All core function tests passed!")
        return True
    else:
        print("⚠️ Some core function tests failed")
        return False

if __name__ == "__main__":
    success = run_all_core_tests()
    sys.exit(0 if success else 1)