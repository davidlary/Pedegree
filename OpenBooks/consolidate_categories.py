#!/usr/bin/env python3

import shutil
from pathlib import Path

def consolidate_categories():
    """Consolidate duplicate categories into simplified names."""
    
    # Define consolidation mapping
    consolidation_plan = [
        # Source directory -> Target directory
        ("Books/english/Arts and Humanities", "Books/english/History"),
        ("Books/english/Biochemistry, Genetics and Molecular Biology", "Books/english/Biology"),
        ("Books/english/Business, Management and Accounting", "Books/english/Business"),
        ("Books/french/Computer science", "Books/french/Computer Science"),
        ("Books/english/Economics, Econometrics and Finance", "Books/english/Economics"),
        ("Books/english/Immunology and Microbiology", "Books/english/Biology"),
        ("Books/english/Physics and Astronomy", "Books/english/Physics"),
        ("Books/english/Social Sciences", "Books/english/Sociology"),
    ]
    
    print("🔄 Starting category consolidation...")
    print("=" * 80)
    
    moved_count = 0
    
    for source_path, target_path in consolidation_plan:
        source = Path(source_path)
        target = Path(target_path)
        
        if not source.exists():
            print(f"⚠️  Source not found: {source}")
            continue
            
        print(f"\n📂 Consolidating: {source.name} -> {target.name}")
        
        # Create target directory if it doesn't exist
        target.mkdir(parents=True, exist_ok=True)
        
        # Move all educational levels
        for level_dir in source.iterdir():
            if not level_dir.is_dir():
                continue
                
            target_level = target / level_dir.name
            target_level.mkdir(parents=True, exist_ok=True)
            
            # Move all repositories in this level
            for repo_dir in level_dir.iterdir():
                if repo_dir.is_dir() and (repo_dir / ".git").exists():
                    target_repo = target_level / repo_dir.name
                    
                    if target_repo.exists():
                        print(f"   ⚠️  {repo_dir.name} already exists in target - skipping")
                    else:
                        try:
                            shutil.move(str(repo_dir), str(target_repo))
                            print(f"   ✅ Moved: {repo_dir.name}")
                            moved_count += 1
                        except Exception as e:
                            print(f"   ❌ Error moving {repo_dir.name}: {e}")
        
        # Remove empty source directory
        try:
            # Remove empty level directories first
            for level_dir in source.iterdir():
                if level_dir.is_dir() and not any(level_dir.iterdir()):
                    level_dir.rmdir()
                    print(f"   🗑️  Removed empty: {level_dir}")
            
            # Remove main source directory if empty
            if not any(source.iterdir()):
                source.rmdir()
                print(f"   🗑️  Removed: {source.name}")
            else:
                print(f"   ⚠️  {source.name} not empty, keeping")
                
        except Exception as e:
            print(f"   ⚠️  Could not remove {source.name}: {e}")
    
    print(f"\n📊 Consolidation complete: Moved {moved_count} repositories")
    return moved_count

def clean_empty_directories():
    """Remove empty category directories."""
    books_dir = Path("Books")
    removed_count = 0
    
    print(f"\n🗑️  Cleaning up empty directories...")
    
    for lang_dir in books_dir.iterdir():
        if not lang_dir.is_dir():
            continue
            
        for subject_dir in lang_dir.iterdir():
            if not subject_dir.is_dir():
                continue
                
            # Check if subject directory is empty or contains only empty subdirs
            has_books = False
            empty_subdirs = []
            
            for level_dir in subject_dir.iterdir():
                if level_dir.is_dir():
                    repos = [d for d in level_dir.iterdir() if d.is_dir() and (d / ".git").exists()]
                    if repos:
                        has_books = True
                    else:
                        empty_subdirs.append(level_dir)
            
            # Remove empty subdirectories
            for empty_dir in empty_subdirs:
                try:
                    empty_dir.rmdir()
                    print(f"   🗑️  Removed empty: {empty_dir}")
                    removed_count += 1
                except Exception as e:
                    print(f"   ⚠️  Could not remove {empty_dir}: {e}")
            
            # Remove main subject directory if no books
            if not has_books:
                try:
                    if not any(subject_dir.iterdir()):
                        subject_dir.rmdir()
                        print(f"   🗑️  Removed empty: {subject_dir}")
                        removed_count += 1
                except Exception as e:
                    print(f"   ⚠️  Could not remove {subject_dir}: {e}")
    
    print(f"📊 Cleanup complete: Removed {removed_count} empty directories")
    return removed_count

def verify_consolidation():
    """Verify the consolidation results."""
    books_dir = Path("Books")
    
    print(f"\n✅ Verifying consolidation results...")
    print("-" * 50)
    
    category_counts = {}
    total_books = 0
    
    for lang_dir in books_dir.iterdir():
        if not lang_dir.is_dir():
            continue
            
        language = lang_dir.name
        
        for subject_dir in lang_dir.iterdir():
            if not subject_dir.is_dir():
                continue
                
            subject = subject_dir.name
            book_count = 0
            
            for level_dir in subject_dir.iterdir():
                if level_dir.is_dir():
                    repos = [d for d in level_dir.iterdir() if d.is_dir() and (d / ".git").exists()]
                    book_count += len(repos)
            
            if book_count > 0:
                key = f"{language}/{subject}"
                category_counts[key] = book_count
                total_books += book_count
    
    # Display results
    for category, count in sorted(category_counts.items()):
        print(f"   {category:<30} {count:>3} books")
    
    print("-" * 50)
    print(f"   {'TOTAL':<30} {total_books:>3} books")
    
    # Check for remaining duplicates
    subjects_only = [cat.split('/')[1] for cat in category_counts.keys()]
    duplicates = []
    seen = set()
    
    for subject in subjects_only:
        simplified = subject.lower().replace(' ', '').replace(',', '')
        if simplified in seen:
            duplicates.append(subject)
        seen.add(simplified)
    
    if duplicates:
        print(f"\n⚠️  Potential remaining duplicates: {duplicates}")
        return False
    else:
        print(f"\n✅ No duplicate categories found")
        return True

if __name__ == "__main__":
    print("🏗️  CATEGORY CONSOLIDATION PROCESS")
    print("=" * 80)
    
    # Step 1: Consolidate categories
    moved = consolidate_categories()
    
    # Step 2: Clean up empty directories
    removed = clean_empty_directories()
    
    # Step 3: Verify results
    success = verify_consolidation()
    
    print("\n" + "=" * 80)
    print("📊 CONSOLIDATION SUMMARY")
    print("=" * 80)
    print(f"✅ Repositories moved: {moved}")
    print(f"🗑️  Directories removed: {removed}")
    print(f"🎯 Verification: {'PASSED' if success else 'FAILED'}")
    
    if success:
        print("\n🎉 Category consolidation completed successfully!")
    else:
        print("\n❌ Category consolidation needs review")
        
    exit(0 if success else 1)