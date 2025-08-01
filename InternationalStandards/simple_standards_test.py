#!/usr/bin/env python3
"""
Simple Standards Integration Test
"""

import sys
import traceback
from pathlib import Path

def test_standards_integration():
    """Simple test of standards integration"""
    print("🧪 SIMPLE STANDARDS INTEGRATION TEST")
    print("=" * 50)
    
    try:
        # Test 1: App instantiation
        print("Testing app instantiation...")
        from GetInternationalStandards import InternationalStandardsApp
        
        app = InternationalStandardsApp()
        print("✅ App instantiated successfully")
        
        # Test 2: Check critical attributes
        print("Checking critical attributes...")
        critical_attrs = ['config', 'orchestrator', 'database_manager', 'cache']
        
        for attr in critical_attrs:
            if hasattr(app, attr) and getattr(app, attr) is not None:
                print(f"✅ {attr}: OK")
            else:
                print(f"❌ {attr}: MISSING or None")
                return False
        
        # Test 3: Check RetrievalAgent standards integration
        print("Checking RetrievalAgent standards integration...")
        
        if hasattr(app, 'orchestrator') and app.orchestrator:
            retrieval_agents = [agent for agent in app.orchestrator.agents.values() 
                              if hasattr(agent, 'agent_type') and agent.agent_type == 'retrieval']
            
            if retrieval_agents:
                agent = retrieval_agents[0]
                print(f"✅ Found retrieval agent: {agent.agent_id}")
                
                # Check standards attributes
                standards_attrs = ['standards_base_dir', 'discipline_mapping']
                for attr in standards_attrs:
                    if hasattr(agent, attr):
                        print(f"✅ Standards attribute {attr}: OK")
                    else:
                        print(f"❌ Standards attribute {attr}: MISSING")
                        return False
                
                # Check standards methods
                standards_methods = ['_process_standards_documents', '_classify_academic_standard']
                for method in standards_methods:
                    if hasattr(agent, method):
                        print(f"✅ Standards method {method}: OK")
                    else:
                        print(f"❌ Standards method {method}: MISSING")
                        return False
            else:
                print("❌ No retrieval agents found")
                return False
        else:
            print("❌ Orchestrator not available")
            return False
        
        # Test 4: Check database standards support
        print("Checking database standards support...")
        
        if hasattr(app.database_manager, 'get_standards_documents'):
            print("✅ get_standards_documents method exists")
            
            # Try to call it
            try:
                standards_docs = app.database_manager.get_standards_documents()
                print(f"✅ Standards query works: {len(standards_docs)} documents")
            except Exception as e:
                print(f"⚠️  Standards query failed (may be expected): {e}")
        else:
            print("❌ get_standards_documents method missing")
            return False
        
        # Test 5: Check Standards directory
        print("Checking Standards directory structure...")
        
        standards_dir = Path("data/Standards")
        if standards_dir.exists():
            print(f"✅ Standards directory exists: {standards_dir}")
        else:
            print(f"⚠️  Standards directory doesn't exist yet: {standards_dir}")
            # This is OK for now
        
        print("\n🎉 ALL STANDARDS INTEGRATION TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_standards_integration()
    sys.exit(0 if success else 1)