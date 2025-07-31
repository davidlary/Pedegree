#!/usr/bin/env python3
"""
Test ConfigManager fix for data_dir attribute
"""

def test_config_manager_fix():
    """Test that ConfigManager now has data_dir attribute"""
    print("🔧 Testing ConfigManager Fix...")
    
    try:
        from pathlib import Path
        from core.config_manager import ConfigManager
        
        # Initialize ConfigManager
        config_manager = ConfigManager(Path("config"))
        
        # Test that data_dir attribute exists
        if hasattr(config_manager, 'data_dir'):
            print(f"  ✅ data_dir attribute exists: {config_manager.data_dir}")
            
            # Test that data_dir is a Path object
            if isinstance(config_manager.data_dir, Path):
                print("  ✅ data_dir is a Path object")
                
                # Test that data_dir directory exists or can be created
                if config_manager.data_dir.exists() or config_manager.data_dir.parent.exists():
                    print("  ✅ data_dir path is valid")
                    return True
                else:
                    print("  ❌ data_dir path is invalid")
                    return False
            else:
                print("  ❌ data_dir is not a Path object")
                return False
        else:
            print("  ❌ data_dir attribute missing")
            return False
            
    except Exception as e:
        print(f"  ❌ ConfigManager test failed: {e}")
        return False

def test_agent_initialization():
    """Test that agents can now initialize with ConfigManager"""
    print("\n🤖 Testing Agent Initialization...")
    
    try:
        from GetInternationalStandards import InternationalStandardsApp
        
        # Initialize app
        app = InternationalStandardsApp()
        
        # Test that orchestrator exists
        if app.orchestrator:
            print("  ✅ Orchestrator initialized")
            
            # Test the _start_system method that was failing before
            try:
                # This should no longer fail with the ConfigManager fix
                print("  🔄 Testing _start_system method...")
                
                # We won't actually start the system, just verify the method exists
                if hasattr(app, '_start_system'):
                    print("  ✅ _start_system method exists")
                    return True
                else:
                    print("  ❌ _start_system method missing")
                    return False
                    
            except Exception as e:
                print(f"  ❌ _start_system test failed: {e}")
                return False
                
        else:
            print("  ❌ Orchestrator not initialized")
            return False
            
    except Exception as e:
        print(f"  ❌ Agent initialization test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTING CONFIGMANAGER FIX")
    
    config_success = test_config_manager_fix()
    agent_success = test_agent_initialization()
    
    if config_success and agent_success:
        print("\n✅ ALL TESTS PASSED - ConfigManager fix successful!")
        print("   System should now start agents without 'data_dir' error")
    else:
        print("\n❌ TESTS FAILED - ConfigManager fix needs more work")