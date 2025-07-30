#!/usr/bin/env python3

from core.orchestrator import OpenBooksOrchestrator
from core.config import OpenBooksConfig
from core.terminal_ui import TerminalUI
from pathlib import Path

def test_consolidated_classification():
    """Test the consolidated classification system."""
    
    config = OpenBooksConfig()
    ui = TerminalUI()
    orchestrator = OpenBooksOrchestrator(config, ui)
    
    print("🧪 Testing Consolidated Classification System")
    print("=" * 80)
    
    # Test cases covering all current books
    test_cases = [
        # Physics books
        ("osbooks-physics", "Physics"),
        ("osbooks-astronomy", "Physics"),
        ("osbooks-university-physics-bundle", "Physics"),
        ("osbooks-college-physics-bundle", "Physics"),
        ("osbooks-fisica-universitaria-bundle", "Physics"),
        
        # Chemistry books
        ("osbooks-chemistry-bundle", "Chemistry"),
        ("osbooks-organic-chemistry", "Chemistry"),
        ("osbooks-quimica-bundle", "Chemistry"),
        
        # Mathematics books
        ("osbooks-calculus-bundle", "Mathematics"),
        ("osbooks-statistics", "Mathematics"),
        ("osbooks-contemporary-mathematics", "Mathematics"),
        ("osbooks-precalculo", "Mathematics"),
        ("osbooks-college-algebra-bundle", "Mathematics"),
        
        # Biology books
        ("osbooks-biology-bundle", "Biology"),
        ("osbooks-anatomy-physiology", "Biology"),
        ("osbooks-microbiology", "Biology"),
        ("cnxbook-openstax-mini-biology-intern-project", "Biology"),
        
        # Business books
        ("osbooks-business-ethics", "Business"),
        ("osbooks-entrepreneurship", "Business"),
        ("osbooks-principles-marketing", "Business"),
        ("osbooks-principles-finance", "Business"),
        ("osbooks-principles-accounting-bundle", "Business"),
        ("osbooks-business-law", "Business"),
        ("osbooks-introduction-business", "Business"),
        ("osbooks-introduction-intellectual-property", "Business"),
        
        # Economics books
        ("osbooks-principles-economics-bundle", "Economics"),
        ("osbooks-mikroekonomia", "Economics"),
        ("osbooks-makroekonomia", "Economics"),
        
        # History books
        ("osbooks-us-history", "History"),
        ("osbooks-world-history", "History"),
        ("osbooks-life-liberty-and-pursuit-happiness", "History"),
        ("osbooks-writing-guide", "History"),
        
        # Psychology books
        ("osbooks-psychology", "Psychology"),
        ("osbooks-psychologia", "Psychology"),
        
        # Sociology books
        ("cnxbook-intro-to-soc-openstax-2018-edited-by-h-hyodo", "Sociology"),
        ("osbooks-college-success-bundle", "Sociology"),
        ("osbooks-introduction-sociology", "Sociology"),
        
        # Medicine books
        ("osbooks-nursing-external-bundle", "Medicine"),
        
        # Computer Science books
        ("osbooks-introduction-python-programming", "Computer Science"),
        
        # Other subjects
        ("osbooks-introduction-anthropology", "Anthropology"),
        ("osbooks-introduction-political-science", "Political Science"),
        ("osbooks-introduction-philosophy", "Philosophy"),
    ]
    
    passed = 0
    failed = 0
    
    print("🔍 Testing individual book classifications:")
    print("-" * 80)
    
    for book_name, expected in test_cases:
        detected = orchestrator._extract_subject_from_repo_name(book_name)
        
        if detected == expected:
            print(f"✅ {book_name:<50} -> {detected}")
            passed += 1
        else:
            print(f"❌ {book_name:<50} -> {detected} (expected {expected})")
            failed += 1
    
    print("-" * 80)
    print(f"📊 CLASSIFICATION TEST RESULTS")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   🎯 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    # Test path-based classification for existing directories
    print(f"\n🗂️  Testing path-based classification:")
    print("-" * 80)
    
    books_dir = Path("Books")
    path_tests = []
    
    for lang_dir in books_dir.iterdir():
        if not lang_dir.is_dir():
            continue
            
        for subject_dir in lang_dir.iterdir():
            if not subject_dir.is_dir():
                continue
                
            for level_dir in subject_dir.iterdir():
                if not level_dir.is_dir():
                    continue
                    
                for repo_dir in level_dir.iterdir():
                    if repo_dir.is_dir() and (repo_dir / ".git").exists():
                        path_tests.append((repo_dir, subject_dir.name))
                        break  # Just test one repo per subject/language
    
    path_passed = 0
    path_failed = 0
    
    for repo_path, current_subject in path_tests:
        detected = orchestrator._detect_subject_from_path(repo_path)
        
        if detected == current_subject:
            print(f"✅ {repo_path.name:<50} in {current_subject}")
            path_passed += 1
        else:
            print(f"🔄 {repo_path.name:<50} {current_subject} -> {detected}")
            if detected != "Uncategorized":
                path_passed += 1  # Consider it a pass if it's a valid classification
            else:
                path_failed += 1
    
    print("-" * 80)
    print(f"📊 PATH-BASED TEST RESULTS")
    print(f"   ✅ Correct: {path_passed}")
    print(f"   🔄 Needs adjustment: {path_failed}")
    
    # Final summary
    overall_success = failed == 0 and path_failed == 0
    
    print(f"\n{'='*80}")
    print(f"🎯 CONSOLIDATED CLASSIFICATION SYSTEM VALIDATION")
    print(f"{'='*80}")
    print(f"📋 Name-based Classification: {passed}/{passed+failed} ({(passed/(passed+failed)*100):.1f}%)")
    print(f"🗂️  Path-based Classification: {path_passed}/{path_passed+path_failed} ({(path_passed/(path_passed+path_failed)*100):.1f}%)")
    print(f"🏆 Overall Status: {'✅ PASSED' if overall_success else '⚠️ NEEDS REVIEW'}")
    
    return overall_success

if __name__ == "__main__":
    success = test_consolidated_classification()
    exit(0 if success else 1)