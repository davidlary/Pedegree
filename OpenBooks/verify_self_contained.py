#!/usr/bin/env python3
"""
Self-Containment Verification Script for ReadOpenBooks

This script verifies that all code and data is present within the current directory
and there are no external dependencies outside of the directory structure.
"""

import os
import sys
from pathlib import Path
import ast
import subprocess

def verify_directory_structure():
    """Verify all required directories and files are present."""
    print("🔍 Verifying directory structure...")
    
    required_items = {
        'ReadOpenBooks.py': 'file',
        'test_installation.py': 'file', 
        'requirements.txt': 'file',
        'README.md': 'file',
        'Books/': 'directory',
        'core/': 'directory',
        'config/': 'directory',
        'tests/': 'directory',
        'metadata/': 'directory',
        'cache/': 'directory'
    }
    
    missing_items = []
    current_dir = Path.cwd()
    
    for item, item_type in required_items.items():
        path = current_dir / item
        if item_type == 'file' and not path.is_file():
            missing_items.append(f"Missing file: {item}")
        elif item_type == 'directory' and not path.is_dir():
            missing_items.append(f"Missing directory: {item}")
    
    if missing_items:
        print("❌ Directory structure incomplete:")
        for item in missing_items:
            print(f"  - {item}")
        return False
    else:
        print("✅ All required directories and files present")
        return True

def check_external_dependencies():
    """Check for external path dependencies in Python files."""
    print("\n🔍 Checking for external dependencies...")
    
    current_dir = Path.cwd()
    python_files = list(current_dir.rglob("*.py"))
    
    external_deps = []
    absolute_paths = []
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for absolute paths outside current directory
            if '/Users/davidlary/Dropbox/Environments/Code' in content:
                lines = content.split('\\n')
                for i, line in enumerate(lines, 1):
                    if '/Users/davidlary/Dropbox/Environments/Code' in line and 'Pedegree/OpenBooks' not in line:
                        absolute_paths.append(f"{py_file.relative_to(current_dir)}:{i}")
            
            # Parse AST to check imports
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if '/' in alias.name or alias.name.startswith('/'):
                                external_deps.append(f"{py_file.relative_to(current_dir)}: import {alias.name}")
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and ('/' in node.module or node.module.startswith('/')):
                            external_deps.append(f"{py_file.relative_to(current_dir)}: from {node.module}")
            except SyntaxError:
                # Skip files with syntax errors
                pass
                
        except Exception as e:
            print(f"⚠️ Could not check {py_file}: {e}")
    
    if external_deps:
        print("❌ Found external import dependencies:")
        for dep in external_deps:
            print(f"  - {dep}")
    
    if absolute_paths:
        print("❌ Found absolute paths outside current directory:")
        for path in absolute_paths:
            print(f"  - {path}")
    
    if not external_deps and not absolute_paths:
        print("✅ No external dependencies found")
        return True
    else:
        return False

def verify_book_collection():
    """Verify the Books directory contains the expected collection."""
    print("\\n🔍 Verifying book collection...")
    
    books_dir = Path.cwd() / "Books"
    if not books_dir.exists():
        print("❌ Books directory missing")
        return False
    
    # Count books and languages
    total_books = 0
    languages = []
    
    for lang_dir in books_dir.iterdir():
        if lang_dir.is_dir() and lang_dir.name not in ['BookList.json', 'BookList.tsv']:
            languages.append(lang_dir.name)
            for subject_dir in lang_dir.iterdir():
                if subject_dir.is_dir():
                    for level_dir in subject_dir.iterdir():
                        if level_dir.is_dir():
                            # Count git repositories
                            repos = [d for d in level_dir.iterdir() if d.is_dir() and (d / '.git').exists()]
                            total_books += len(repos)
    
    print(f"✅ Found {total_books} books across {len(languages)} languages")
    print(f"✅ Languages: {sorted(languages)}")
    
    if total_books >= 40:  # Should have ~48 books
        return True
    else:
        print(f"⚠️ Expected ~48 books, found {total_books}")
        return False

def test_autonomous_execution():
    """Test that ReadOpenBooks.py can run autonomously."""
    print("\\n🔍 Testing autonomous execution...")
    
    current_dir = Path.cwd()
    
    # Test Python import without execution
    try:
        cmd = [sys.executable, '-c', 
               f"import sys; sys.path.insert(0, '{current_dir}'); "
               "from core.config import OpenBooksConfig; "
               "from core.orchestrator import OpenBooksOrchestrator; "
               "print('✅ Core modules import successfully')"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Core modules can be imported autonomously")
        else:
            print(f"❌ Core module import failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Import test timed out")
        return False
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    # Test Streamlit application syntax
    try:
        with open('ReadOpenBooks.py', 'r') as f:
            content = f.read()
        
        compile(content, 'ReadOpenBooks.py', 'exec')
        print("✅ ReadOpenBooks.py syntax is valid")
        
    except SyntaxError as e:
        print(f"❌ ReadOpenBooks.py syntax error: {e}")
        return False
    
    return True

def main():
    """Run all verification tests."""
    print("🚀 ReadOpenBooks Self-Containment Verification")
    print("=" * 50)
    
    current_dir = Path.cwd()
    print(f"Testing directory: {current_dir}")
    
    if not str(current_dir).endswith('Pedegree/OpenBooks'):
        print("⚠️ Warning: Not running from expected directory")
        print("Expected: .../Pedegree/OpenBooks")
    
    tests = [
        ("Directory Structure", verify_directory_structure),
        ("External Dependencies", check_external_dependencies),
        ("Book Collection", verify_book_collection),
        ("Autonomous Execution", test_autonomous_execution)
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
    print("\\n" + "=" * 50)
    print("📊 Self-Containment Verification Results")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All verification tests passed!")
        print("✅ ReadOpenBooks is completely self-contained")
        print("✅ No external dependencies detected")
        print("✅ System ready for autonomous operation")
        return True
    else:
        print("⚠️ Some verification tests failed")
        print("❌ System may have external dependencies")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)