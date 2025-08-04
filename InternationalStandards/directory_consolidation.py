#!/usr/bin/env python3
"""
Directory Consolidation Script for International Standards System
Part of CRITICAL FIX 2: Directory Structure Consolidation

This script consolidates the parallel directory structures:
- /data/Standards/english/ (primary)
- /data/processed/ (secondary - to be merged)
- /data/validation/ (tertiary - to be merged)
"""

import os
import shutil
from pathlib import Path
import json
from datetime import datetime

def consolidate_directory_structures():
    """Consolidate parallel directory structures into Standards/english/"""
    
    print("🔥 EXECUTING DIRECTORY CONSOLIDATION")
    print("🎯 TARGET: Merge all parallel structures into Standards/english/")
    
    # Define base directories
    data_dir = Path(__file__).parent / "data"
    primary_dir = data_dir / "Standards" / "english"  # Target directory
    secondary_dirs = [
        data_dir / "processed",
        data_dir / "validation"
    ]
    
    consolidation_report = {
        'timestamp': datetime.now().isoformat(),
        'operation': 'directory_consolidation',
        'files_moved': 0,
        'files_duplicates': 0,
        'directories_merged': 0,
        'errors': []
    }
    
    # Ensure primary directory exists
    primary_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Primary directory: {primary_dir}")
    
    # Process each secondary directory
    for secondary_dir in secondary_dirs:
        if not secondary_dir.exists():
            print(f"⚠️ Secondary directory does not exist: {secondary_dir}")
            continue
            
        print(f"🔄 Processing secondary directory: {secondary_dir}")
        
        # Walk through all files in secondary directory
        for root, dirs, files in os.walk(secondary_dir):
            root_path = Path(root)
            
            # Calculate relative path from secondary directory
            relative_path = root_path.relative_to(secondary_dir)
            
            # Create corresponding directory in primary
            target_dir = primary_dir / relative_path
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Move each file
            for file in files:
                source_file = root_path / file
                target_file = target_dir / file
                
                try:
                    if target_file.exists():
                        # Handle duplicates - keep larger file
                        source_size = source_file.stat().st_size
                        target_size = target_file.stat().st_size
                        
                        if source_size > target_size:
                            print(f"🔄 Replacing smaller duplicate: {target_file.name}")
                            shutil.move(str(source_file), str(target_file))
                            consolidation_report['files_moved'] += 1
                        else:
                            print(f"📄 Keeping existing larger file: {target_file.name}")
                            source_file.unlink()  # Remove smaller duplicate
                        
                        consolidation_report['files_duplicates'] += 1
                    else:
                        # Move file to target
                        shutil.move(str(source_file), str(target_file))
                        consolidation_report['files_moved'] += 1
                        print(f"📄 Moved: {relative_path / file}")
                        
                except Exception as e:
                    error_msg = f"Error moving {source_file} to {target_file}: {str(e)}"
                    print(f"❌ {error_msg}")
                    consolidation_report['errors'].append(error_msg)
        
        # Remove empty secondary directory structure
        try:
            if secondary_dir.exists() and len(list(secondary_dir.rglob('*'))) == 0:
                shutil.rmtree(secondary_dir)
                print(f"🗑️ Removed empty secondary directory: {secondary_dir}")
                consolidation_report['directories_merged'] += 1
        except Exception as e:
            error_msg = f"Error removing secondary directory {secondary_dir}: {str(e)}"
            print(f"❌ {error_msg}")
            consolidation_report['errors'].append(error_msg)
    
    # Save consolidation report
    report_file = data_dir / f"directory_consolidation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(consolidation_report, f, indent=2)
    
    print("✅ DIRECTORY CONSOLIDATION COMPLETED")
    print(f"📊 Files moved: {consolidation_report['files_moved']}")
    print(f"📊 Duplicates handled: {consolidation_report['files_duplicates']}")
    print(f"📊 Directories merged: {consolidation_report['directories_merged']}")
    print(f"📊 Errors: {len(consolidation_report['errors'])}")
    print(f"📄 Report saved: {report_file}")
    
    return consolidation_report

def verify_consolidation():
    """Verify the consolidation was successful"""
    
    print("🔍 VERIFYING DIRECTORY CONSOLIDATION")
    
    data_dir = Path(__file__).parent / "data"
    primary_dir = data_dir / "Standards" / "english"
    
    # Count files by discipline
    discipline_counts = {}
    total_files = 0
    
    for discipline_dir in primary_dir.glob('*'):
        if discipline_dir.is_dir():
            file_count = len(list(discipline_dir.rglob('*.pdf'))) + len(list(discipline_dir.rglob('*.html')))
            discipline_counts[discipline_dir.name] = file_count
            total_files += file_count
    
    print(f"📊 Total documents in consolidated structure: {total_files}")
    print("📋 Documents by discipline:")
    for discipline, count in sorted(discipline_counts.items()):
        if count > 0:
            print(f"   {discipline}: {count} documents")
    
    # Check for remaining parallel directories
    parallel_dirs = [data_dir / "processed", data_dir / "validation"]
    remaining_parallels = [d for d in parallel_dirs if d.exists() and len(list(d.rglob('*'))) > 0]
    
    if remaining_parallels:
        print("⚠️ WARNING: Parallel directories still contain content:")
        for dir_path in remaining_parallels:
            file_count = len(list(dir_path.rglob('*')))
            print(f"   {dir_path}: {file_count} items")
    else:
        print("✅ SUCCESS: No remaining parallel directory structures")
    
    return {
        'total_files': total_files,
        'discipline_counts': discipline_counts,
        'remaining_parallels': len(remaining_parallels)
    }

if __name__ == "__main__":
    # Execute consolidation
    consolidation_report = consolidate_directory_structures()
    
    # Verify results
    verification_report = verify_consolidation()
    
    # Final status
    if len(consolidation_report['errors']) == 0 and verification_report['remaining_parallels'] == 0:
        print("🎉 CRITICAL FIX 2: DIRECTORY CONSOLIDATION COMPLETED SUCCESSFULLY")
    else:
        print("⚠️ CRITICAL FIX 2: DIRECTORY CONSOLIDATION COMPLETED WITH ISSUES")