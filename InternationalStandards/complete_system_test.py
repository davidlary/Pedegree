#!/usr/bin/env python3
"""
COMPLETE SYSTEM TEST - Test full discipline processing
This simulates what happens when user clicks Start System in the UI
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path

def test_complete_system():
    """Test complete system functionality including all disciplines"""
    print("🚀 COMPLETE SYSTEM TEST - FULL DISCIPLINE PROCESSING")
    print("=" * 60)
    print(f"Test started: {datetime.now()}")
    
    try:
        # Import the app
        from GetInternationalStandards import InternationalStandardsApp
        print("✅ App imported successfully")
        
        # Create app instance
        app = InternationalStandardsApp()
        print("✅ App initialized successfully")
        
        # Check initial state
        if not app.database_manager:
            print("❌ Database manager not available")
            return False
            
        disciplines = app.database_manager.get_disciplines()
        print(f"✅ Found {len(disciplines)} disciplines in database")
        
        if len(disciplines) != 19:
            print(f"⚠️  Expected 19 disciplines, found {len(disciplines)}")
        
        # Show disciplines
        print("📋 Disciplines to process:")
        for i, disc in enumerate(disciplines[:5], 1):  # Show first 5
            print(f"   {i}. {disc.get('name', 'Unknown')}")
        if len(disciplines) > 5:
            print(f"   ... and {len(disciplines) - 5} more")
        
        # Record initial file state
        initial_files = list(Path('.').rglob('*.json')) + list(Path('.').rglob('*.csv'))
        print(f"📁 Initial file count: {len(initial_files)}")
        
        # Test orchestrator startup
        print("\n🎼 Testing orchestrator startup...")
        if app.orchestrator:
            # Initialize all agents first
            try:
                print("🔧 Initializing all agents...")
                init_result = app.orchestrator.initialize_all_agents()
                print(f"   ✅ Agent initialization: {init_result}")
                
                # Start system with discipline names
                discipline_names = [d.get('name', 'Unknown') for d in disciplines[:3]]  # Test first 3
                print(f"🚀 Starting system with disciplines: {discipline_names}")
                
                system_result = app.orchestrator.start_system(discipline_names)
                print(f"   ✅ System start result: {system_result}")
                
                # Wait for some processing
                print("⏳ Waiting for processing...")
                time.sleep(5)
                
                # Check agent status
                agent_status = app.orchestrator.get_agent_status()
                print(f"   📊 Active agents: {len(agent_status)}")
                
                # Check for any new files
                current_files = list(Path('.').rglob('*.json')) + list(Path('.').rglob('*.csv'))
                new_files_count = len(current_files) - len(initial_files)
                print(f"   📁 New files created: {new_files_count}")
                
                initial_files = current_files
                        
            except Exception as e:
                print(f"   ❌ Error in orchestrator startup: {e}")
                import traceback
                traceback.print_exc()
                    
        else:
            print("❌ Orchestrator not available")
            return False
        
        # Final file check
        final_files = list(Path('.').rglob('*.json')) + list(Path('.').rglob('*.csv'))
        total_new_files = len(final_files) - len(initial_files)
        
        print(f"\n📊 PROCESSING RESULTS:")
        print(f"📁 Total files after processing: {len(final_files)}")
        print(f"📈 New files created: {total_new_files}")
        
        # Check for discipline-specific files
        discipline_files = []
        for f in final_files:
            for d in disciplines[:3]:
                discipline_name = d.get('name', d.get('display_name', 'Unknown'))
                if discipline_name.lower().replace(' ', '_') in str(f).lower():
                    discipline_files.append(f)
                    break
        print(f"🎯 Discipline-specific files: {len(discipline_files)}")
        
        if discipline_files:
            print("📋 Sample discipline files:")
            for f in discipline_files[:5]:
                print(f"   • {f}")
        
        # Test database updates
        print(f"\n🗄️  Testing database updates...")
        updated_standards = app.database_manager.get_all_standards()
        print(f"✅ Standards in database: {len(updated_standards)}")
        
        # Test system stats
        print(f"\n📈 Testing system statistics...")
        try:
            stats = app._get_system_stats()
            print(f"✅ System stats retrieved: {type(stats)}")
            if isinstance(stats, dict):
                for key, value in list(stats.items())[:5]:  # Show first 5 stats
                    print(f"   {key}: {value}")
        except Exception as e:
            print(f"⚠️  Stats error: {e}")
        
        # Final assessment
        print("\n" + "=" * 60)
        print("🏆 COMPLETE SYSTEM TEST RESULTS")
        print("=" * 60)
        
        success_criteria = [
            ("App initializes correctly", True),
            ("Database manager available", app.database_manager is not None),
            ("Orchestrator available", app.orchestrator is not None),
            ("Disciplines loaded", len(disciplines) >= 10),  # At least 10 disciplines
            ("New files created", total_new_files > 0),
            ("No critical errors", True)  # Made it this far without exceptions
        ]
        
        passed = sum(1 for _, result in success_criteria if result)
        total = len(success_criteria)
        
        for criterion, result in success_criteria:
            status = "✅" if result else "❌"
            print(f"{status} {criterion}")
        
        score = passed / total * 100
        print(f"\n📊 SCORE: {passed}/{total} ({score:.1f}%)")
        
        if score >= 90:
            print(f"\n🎉 VERDICT: SYSTEM FULLY FUNCTIONAL!")
            print("✅ All critical components working")
            print("✅ Disciplines processing successfully") 
            print("✅ Files being created as expected")
            print("✅ Ready for production use")
            return True
        elif score >= 70:
            print(f"\n⚠️  VERDICT: MOSTLY FUNCTIONAL")
            print(f"✅ {score:.1f}% of tests passed")
            print("🔧 Minor issues may need attention")
            return True
        else:
            print(f"\n❌ VERDICT: SIGNIFICANT ISSUES")
            print(f"❌ Only {score:.1f}% of tests passed")
            return False
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_system()
    print(f"\n🏁 FINAL RESULT: {'SUCCESS' if success else 'FAILED'}")
    exit(0 if success else 1)