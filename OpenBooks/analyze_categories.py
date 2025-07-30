#!/usr/bin/env python3

from pathlib import Path
from collections import defaultdict

def analyze_category_duplications():
    """Analyze current category structure and identify duplications."""
    
    books_dir = Path("Books")
    category_analysis = defaultdict(list)
    duplicate_issues = []
    
    print("🔍 Analyzing current category structure...")
    print("=" * 80)
    
    # Collect all categories with book counts
    for lang_dir in books_dir.iterdir():
        if not lang_dir.is_dir():
            continue
            
        language = lang_dir.name
        
        for subject_dir in lang_dir.iterdir():
            if not subject_dir.is_dir():
                continue
                
            subject = subject_dir.name
            book_count = 0
            
            # Count books in all levels
            for level_dir in subject_dir.iterdir():
                if level_dir.is_dir():
                    repos = [d for d in level_dir.iterdir() if d.is_dir() and (d / ".git").exists()]
                    book_count += len(repos)
            
            if book_count > 0:
                category_analysis[subject].append({
                    'language': language,
                    'path': str(subject_dir),
                    'book_count': book_count
                })
    
    # Identify consolidation opportunities
    consolidation_map = {
        # Physics consolidation
        "Physics and Astronomy": "Physics",
        
        # Business consolidation  
        "Business, Management and Accounting": "Business",
        
        # Economics consolidation
        "Economics, Econometrics and Finance": "Economics",
        
        # Biology consolidation
        "Biochemistry, Genetics and Molecular Biology": "Biology",
        "Immunology and Microbiology": "Biology",
        
        # Social Sciences consolidation
        "Social Sciences": "Sociology",
        
        # Arts consolidation
        "Arts and Humanities": "History",
        
        # Computer Science standardization
        "Computer science": "Computer Science"
    }
    
    print("📊 CURRENT CATEGORY DISTRIBUTION")
    print("-" * 80)
    
    total_categories = 0
    total_books = 0
    
    for category, instances in sorted(category_analysis.items()):
        total_categories += 1
        category_books = sum(inst['book_count'] for inst in instances)
        total_books += category_books
        
        print(f"{category:<40} {category_books:>3} books")
        for instance in instances:
            print(f"  └─ {instance['language']:<12} {instance['book_count']:>2} books - {instance['path']}")
            
        # Check if this category should be consolidated
        if category in consolidation_map:
            target = consolidation_map[category]
            print(f"  🔄 CONSOLIDATE TO: {target}")
            duplicate_issues.append((category, target, instances))
            
        print()
    
    print("=" * 80)
    print(f"📈 SUMMARY: {total_categories} categories, {total_books} total books")
    
    # Show consolidation plan
    if duplicate_issues:
        print(f"\n🔧 CONSOLIDATION PLAN ({len(duplicate_issues)} merges needed)")
        print("-" * 80)
        
        for source, target, instances in duplicate_issues:
            books_to_move = sum(inst['book_count'] for inst in instances)
            print(f"📂 {source} -> {target} ({books_to_move} books)")
            for instance in instances:
                print(f"   Move: {instance['path']} ({instance['book_count']} books)")
    
    return duplicate_issues, consolidation_map

def show_empty_categories():
    """Show categories with no books."""
    books_dir = Path("Books")
    empty_categories = []
    
    for lang_dir in books_dir.iterdir():
        if not lang_dir.is_dir():
            continue
            
        for subject_dir in lang_dir.iterdir():
            if not subject_dir.is_dir():
                continue
                
            has_books = False
            for level_dir in subject_dir.iterdir():
                if level_dir.is_dir():
                    repos = [d for d in level_dir.iterdir() if d.is_dir() and (d / ".git").exists()]
                    if repos:
                        has_books = True
                        break
            
            if not has_books:
                empty_categories.append(str(subject_dir))
    
    if empty_categories:
        print(f"\n🗑️  EMPTY CATEGORIES TO REMOVE ({len(empty_categories)})")
        print("-" * 80)
        for empty in sorted(empty_categories):
            print(f"   {empty}")
    
    return empty_categories

if __name__ == "__main__":
    duplicates, consolidation_map = analyze_category_duplications()
    empty = show_empty_categories()
    
    print(f"\n✅ Analysis complete:")
    print(f"   - {len(duplicates)} consolidation opportunities")
    print(f"   - {len(empty)} empty directories to clean up")