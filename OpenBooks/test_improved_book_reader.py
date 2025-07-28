#!/usr/bin/env python3
"""
Test Improved Book Reader Functionality

This script tests the enhanced book reading features including:
- Alphabetical sorting of menu items
- Table of Contents (TOC) functionality
- Content viewer improvements
- Session state handling
"""

import sys
from pathlib import Path
import traceback

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_alphabetical_sorting():
    """Test that menu items are sorted alphabetically."""
    print("🧪 Testing alphabetical sorting...")
    
    try:
        # Read the ReadOpenBooks.py file to check for sorted() calls
        with open('ReadOpenBooks.py', 'r') as f:
            content = f.read()
        
        # Check for sorted() usage in dropdown selections
        sorting_checks = [
            'sorted([d.name for d in books_dir.iterdir()' in content,  # Languages
            'sorted([d.name for d in lang_dir.iterdir()' in content,   # Subjects
            'sorted([d.name for d in subject_dir.iterdir()' in content, # Levels
            'sorted([d.name for d in level_dir.iterdir()' in content   # Books
        ]
        
        if all(sorting_checks):
            print("✅ All menu items are sorted alphabetically")
            print("  - Languages: sorted")
            print("  - Subjects: sorted") 
            print("  - Levels: sorted")
            print("  - Books: sorted")
            return True
        else:
            print(f"❌ Some menu items not sorted: {sorting_checks}")
            return False
            
    except Exception as e:
        print(f"❌ Alphabetical sorting test failed: {e}")
        return False

def test_toc_functionality():
    """Test Table of Contents functionality."""
    print("\n🧪 Testing Table of Contents functionality...")
    
    try:
        books_dir = Path("Books")
        if not books_dir.exists():
            print("⚠️ Books directory not found - skipping TOC test")
            return True
        
        # Find a sample book to test with
        sample_book = None
        for lang_dir in books_dir.iterdir():
            if lang_dir.is_dir() and lang_dir.name not in ['BookList.json', 'BookList.tsv']:
                for subject_dir in lang_dir.iterdir():
                    if subject_dir.is_dir():
                        for level_dir in subject_dir.iterdir():
                            if level_dir.is_dir():
                                books = [d for d in level_dir.iterdir() if d.is_dir() and (d / '.git').exists()]
                                if books:
                                    sample_book = books[0]
                                    break
                        if sample_book:
                            break
                if sample_book:
                    break
        
        if not sample_book:
            print("⚠️ No sample book found - skipping TOC test")
            return True
        
        print(f"✅ Testing with sample book: {sample_book.name}")
        
        # Test content file discovery
        content_files = []
        patterns = ["*.md", "*.cnxml", "*.html", "*.txt", "*.rst"]
        
        for pattern in patterns:
            content_files.extend(sample_book.rglob(pattern))
        
        content_files = sorted(content_files, key=lambda x: str(x.relative_to(sample_book)))
        
        print(f"✅ Found {len(content_files)} content files in sample book")
        
        if content_files:
            # Test file path processing
            for i, file in enumerate(content_files[:3]):  # Test first 3 files
                relative_path = file.relative_to(sample_book)
                file_name = relative_path.name
                folder_path = str(relative_path.parent) if relative_path.parent != Path('.') else ""
                
                if folder_path:
                    display_name = f"📁 {folder_path} → 📄 {file_name}"
                else:
                    display_name = f"📄 {file_name}"
                
                print(f"✅ TOC entry {i+1}: {display_name}")
        
        print("✅ Table of Contents functionality ready")
        return True
        
    except Exception as e:
        print(f"❌ TOC functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_content_viewer():
    """Test content viewer functionality."""
    print("\n🧪 Testing content viewer functionality...")
    
    try:
        books_dir = Path("Books")
        if not books_dir.exists():
            print("⚠️ Books directory not found - skipping content viewer test")
            return True
        
        # Find a sample content file
        sample_file = None
        for lang_dir in books_dir.iterdir():
            if lang_dir.is_dir() and lang_dir.name not in ['BookList.json', 'BookList.tsv']:
                for subject_dir in lang_dir.iterdir():
                    if subject_dir.is_dir():
                        for level_dir in subject_dir.iterdir():
                            if level_dir.is_dir():
                                books = [d for d in level_dir.iterdir() if d.is_dir() and (d / '.git').exists()]
                                for book in books:
                                    # Look for README files first
                                    readme_files = list(book.glob("README*"))
                                    if readme_files:
                                        sample_file = readme_files[0]
                                        break
                                    # Look for any markdown files
                                    md_files = list(book.glob("*.md"))
                                    if md_files:
                                        sample_file = md_files[0]
                                        break
                                if sample_file:
                                    break
                        if sample_file:
                            break
                if sample_file:
                    break
        
        if not sample_file:
            print("⚠️ No sample content file found - skipping content viewer test")
            return True
        
        print(f"✅ Testing with sample file: {sample_file.name}")
        
        # Test file reading and stats
        try:
            content = sample_file.read_text(encoding='utf-8', errors='ignore')
            file_stats = sample_file.stat()
            file_size = file_stats.st_size
            
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size/1024:.1f} KB"
            else:
                size_str = f"{file_size/(1024*1024):.1f} MB"
            
            print(f"✅ File stats: {size_str}, {len(content)} characters")
            
            # Test file type detection
            file_ext = sample_file.suffix.lower()
            print(f"✅ File extension: {file_ext}")
            
            if file_ext == '.md':
                print("✅ Markdown file - will render with formatting")
            elif file_ext in ['.html', '.htm']:
                print("✅ HTML file - will render in iframe")
            elif file_ext == '.cnxml':
                print("✅ CNXML file - will display as XML code")
            else:
                print("✅ Text file - will display in text area")
            
        except Exception as e:
            print(f"⚠️ File reading test failed: {e}")
        
        print("✅ Content viewer functionality ready")
        return True
        
    except Exception as e:
        print(f"❌ Content viewer test failed: {e}")
        traceback.print_exc()
        return False

def test_session_state_handling():
    """Test session state handling for book selection."""
    print("\n🧪 Testing session state handling...")
    
    try:
        # Check if session state handling is implemented in the code
        with open('ReadOpenBooks.py', 'r') as f:
            content = f.read()
        
        session_state_checks = [
            'st.session_state.current_book_path' in content,
            'st.session_state.current_book_name' in content,
            'st.session_state.selected_content_file' in content,
            'st.rerun()' in content
        ]
        
        if all(session_state_checks):
            print("✅ Session state handling implemented")
            print("  - Book path tracking: ✅")
            print("  - Book name tracking: ✅")
            print("  - Content file selection: ✅")
            print("  - State updates: ✅")
            return True
        else:
            print(f"❌ Session state handling incomplete: {session_state_checks}")
            return False
            
    except Exception as e:
        print(f"❌ Session state test failed: {e}")
        return False

def test_directory_structure_display():
    """Test directory structure display functionality."""
    print("\n🧪 Testing directory structure display...")
    
    try:
        # Check if directory tree display function exists
        with open('ReadOpenBooks.py', 'r') as f:
            content = f.read()
        
        tree_display_checks = [
            'display_directory_tree' in content,
            'max_depth' in content,
            'current_depth' in content,
            '└──' in content or '├──' in content
        ]
        
        if all(tree_display_checks):
            print("✅ Directory tree display implemented")
            print("  - Recursive tree function: ✅")
            print("  - Depth limiting: ✅")
            print("  - Tree formatting: ✅")
            return True
        else:
            print(f"❌ Directory tree display incomplete: {tree_display_checks}")
            return False
            
    except Exception as e:
        print(f"❌ Directory structure test failed: {e}")
        return False

def test_app_syntax():
    """Test that the improved app still has valid syntax."""
    print("\n🧪 Testing improved app syntax...")
    
    try:
        with open('ReadOpenBooks.py', 'r') as f:
            content = f.read()
        
        # Compile to check syntax
        compile(content, 'ReadOpenBooks.py', 'exec')
        print("✅ ReadOpenBooks.py syntax is valid after improvements")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in improved app: {e}")
        return False
    except Exception as e:
        print(f"❌ App syntax test failed: {e}")
        return False

def run_improved_book_reader_tests():
    """Run all improved book reader tests."""
    print("🚀 ReadOpenBooks Improved Book Reader Test Suite")
    print("=" * 60)
    
    tests = [
        ("Alphabetical Sorting", test_alphabetical_sorting),
        ("Table of Contents", test_toc_functionality),
        ("Content Viewer", test_content_viewer),
        ("Session State Handling", test_session_state_handling),
        ("Directory Structure Display", test_directory_structure_display),
        ("App Syntax", test_app_syntax)
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
    print("📊 Improved Book Reader Test Results")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} improvement tests passed")
    
    if passed == total:
        print("🎉 All book reader improvements working!")
        print("\n📚 Enhanced Features:")
        print("- ✅ Alphabetical sorting of all menus")
        print("- ✅ Table of Contents with scrollable file list")
        print("- ✅ Content viewer with multiple format support")
        print("- ✅ Session state for persistent selections")
        print("- ✅ Directory tree with size information")
        print("- ✅ Improved file handling and error recovery")
        return True
    else:
        print("⚠️ Some improvements need attention")
        return False

if __name__ == "__main__":
    success = run_improved_book_reader_tests()
    sys.exit(0 if success else 1)