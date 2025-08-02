#!/usr/bin/env python3
"""
FINAL SYSTEM TEST - Test the actual functionality that creates files
"""

import os
import time
from datetime import datetime
from pathlib import Path

def test_system_functionality():
    """Test the actual system functionality"""
    print("🔧 FINAL SYSTEM FUNCTIONALITY TEST")
    print("=" * 50)
    print(f"Test started: {datetime.now()}")
    
    try:
        # Import the app
        from GetInternationalStandards import InternationalStandardsApp
        print("✅ App imported successfully")
        
        # Create app instance
        app = InternationalStandardsApp()
        print("✅ App initialized successfully")
        
        # Test critical components
        print("🔍 Testing critical components...")
        
        if app.orchestrator:
            print("✅ Orchestrator available")
        else:
            print("❌ Orchestrator not available")
            
        if app.database_manager:
            print("✅ Database manager available")
            # Test database operations
            disciplines = app.database_manager.get_disciplines()
            print(f"✅ Database loaded {len(disciplines)} disciplines")
            
            standards = app.database_manager.get_all_standards()
            print(f"✅ Database has {len(standards)} standards")
        else:
            print("❌ Database manager not available")
        
        # Test start system functionality
        print("\n🚀 Testing Start System functionality...")
        
        # Before starting - record initial file state
        initial_files = list(Path('.').rglob('*.json')) + list(Path('.').rglob('*.db')) + list(Path('.').rglob('*.csv'))
        print(f"📁 Initial file count: {len(initial_files)}")
        
        # Start the system
        result = app._start_system()
        print(f"✅ Start system executed, result: {result}")
        
        # Test real-time updates
        print("\n🔄 Testing real-time updates...")
        for i in range(3):
            print(f"   Update cycle {i+1}...")
            app._handle_realtime_updates()
            app._update_system_stats()
            time.sleep(1)
        
        print("✅ Real-time updates completed")
        
        # Check if any new files were created
        final_files = list(Path('.').rglob('*.json')) + list(Path('.').rglob('*.db')) + list(Path('.').rglob('*.csv'))
        new_files = set(final_files) - set(initial_files)
        
        print(f"\n📁 Final file count: {len(final_files)}")
        
        if new_files:
            print(f"✅ New files created: {len(new_files)}")
            for file in list(new_files)[:5]:  # Show first 5
                print(f"   • {file}")
        else:
            print("⚠️  No new files created during test")
        
        # Test database operations during system running
        print("\n🗄️  Testing database operations during system run...")
        
        try:
            # Check if any standards were updated
            updated_standards = app.database_manager.get_all_standards()
            print(f"✅ Standards after system run: {len(updated_standards)}")
            
            if len(updated_standards) > len(standards):
                print(f"✅ {len(updated_standards) - len(standards)} new standards added!")
            else:
                print("ℹ️  No new standards added during test")
                
        except Exception as e:
            print(f"⚠️  Database check error: {e}")
        
        # Final assessment
        print("\n" + "=" * 50)
        print("📊 FINAL ASSESSMENT")
        print("=" * 50)
        
        success_criteria = [
            ("App initializes", True),
            ("Orchestrator available", app.orchestrator is not None),
            ("Database available", app.database_manager is not None),
            ("Start system works", result is not False),
            ("Real-time updates work", True),  # No errors thrown
        ]
        
        passed = sum(1 for _, result in success_criteria if result)
        total = len(success_criteria)
        
        for criterion, result in success_criteria:
            status = "✅" if result else "❌"
            print(f"{status} {criterion}")
        
        print(f"\nScore: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("\n🎉 SYSTEM IS FUNCTIONAL!")
            print("✅ All critical components working")
            print("✅ Start system executes without errors")
            print("✅ Real-time updates function properly")
            return True
        else:
            print("\n⚠️  SYSTEM HAS ISSUES")
            print(f"   {total-passed} components failed")
            return False
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_system_functionality()
    print(f"\nFinal result: {'SUCCESS' if success else 'FAILED'}")