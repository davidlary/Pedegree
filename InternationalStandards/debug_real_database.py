#!/usr/bin/env python3
"""Debug the real database manager"""

import sys
from pathlib import Path

try:
    from data.database_manager import DatabaseManager, DatabaseConfig
    print("✅ Real DatabaseManager imported successfully")
    
    # Create config
    db_config = DatabaseConfig(
        database_type='sqlite',
        sqlite_path=str(Path('.') / 'international_standards.db')
    )
    
    # Create database manager
    db_manager = DatabaseManager(db_config)
    print("✅ DatabaseManager created")
    
    # Test disciplines loading
    disciplines = db_manager.get_disciplines()
    print(f"📊 Real DatabaseManager returned {len(disciplines)} disciplines")
    
    if disciplines:
        for i, disc in enumerate(disciplines[:3]):
            print(f"Discipline {i+1}: {disc}")
    else:
        print("❌ No disciplines returned from real DatabaseManager")
        
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("🔄 Falling back to TemporaryDatabaseManager...")
    
    # Test the temporary manager
    from GetInternationalStandards import InternationalStandardsApp
    app = InternationalStandardsApp()
    disciplines = app.database_manager.get_disciplines()
    print(f"📊 TemporaryDatabaseManager returned {len(disciplines)} disciplines")
    
    if disciplines:
        for i, disc in enumerate(disciplines[:3]):
            print(f"Discipline {i+1}: {disc}")
    
except Exception as e:
    print(f"💥 Error: {e}")
    import traceback
    traceback.print_exc()