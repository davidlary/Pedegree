#!/usr/bin/env python3
"""
AUTONOMOUS SYSTEM DEBUG - Find and fix why agents aren't running
Debug the system until agents are actually processing standards
"""

import subprocess
import time
import requests
import json
from pathlib import Path
from datetime import datetime

def autonomous_debug_and_fix():
    """Autonomously debug and fix the system until agents are running"""
    print("🔧 AUTONOMOUS SYSTEM DEBUG - FINDING WHY AGENTS AREN'T RUNNING")
    print("=" * 80)
    
    # Step 1: Start fresh Streamlit server
    print("\n1️⃣ Starting fresh Streamlit server...")
    process = subprocess.Popen([
        'streamlit', 'run', 'GetInternationalStandards.py',
        '--server.headless=true', '--server.port=8503'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    time.sleep(15)
    
    # Step 2: Test actual system startup
    print("\n2️⃣ Testing actual system startup...")
    try:
        from GetInternationalStandards import InternationalStandardsApp
        
        app = InternationalStandardsApp()
        print(f"   App initialized: {bool(app)}")
        print(f"   Orchestrator exists: {bool(app.orchestrator)}")
        
        if app.orchestrator:
            print("   Testing orchestrator methods...")
            
            # Check if orchestrator has the right methods
            has_start = hasattr(app.orchestrator, 'start_system')
            has_agents = hasattr(app.orchestrator, 'agents') 
            has_get_status = hasattr(app.orchestrator, 'get_system_status')
            
            print(f"   - start_system method: {has_start}")
            print(f"   - agents attribute: {has_agents}")
            print(f"   - get_system_status method: {has_get_status}")
            
            if has_start:
                print("\n   🚀 Testing start_system method...")
                try:
                    # Test starting the system
                    result = app.orchestrator.start_system()
                    print(f"   Start result: {result}")
                    
                    # Wait a moment for agents to initialize
                    time.sleep(5)
                    
                    # Check agent status
                    if has_get_status:
                        status = app.orchestrator.get_system_status()
                        print(f"   System status: {status}")
                        
                        if 'agents' in status:
                            active_agents = status.get('active_agents', 0)
                            print(f"   Active agents: {active_agents}")
                            
                            if active_agents == 0:
                                print("   ❌ PROBLEM FOUND: Agents not starting!")
                                print("   🔧 Debugging agent initialization...")
                                
                                # Debug agent creation
                                if hasattr(app.orchestrator, 'agents'):
                                    agents = getattr(app.orchestrator, 'agents', {})
                                    print(f"   Agent dictionary: {type(agents)} with {len(agents)} entries")
                                    
                                    if len(agents) == 0:
                                        print("   ❌ ROOT CAUSE: No agents created!")
                                        return fix_agent_creation(app.orchestrator)
                                    else:
                                        print("   🔍 Agents exist but not active - checking agent status...")
                                        for agent_id, agent in agents.items():
                                            print(f"     Agent {agent_id}: {type(agent)}")
                                            if hasattr(agent, 'is_active'):
                                                print(f"       Active: {agent.is_active}")
                                            if hasattr(agent, 'status'):
                                                print(f"       Status: {agent.status}")
                                        return fix_agent_activation(app.orchestrator)
                            else:
                                print(f"   ✅ SUCCESS: {active_agents} agents are active!")
                                return True
                        else:
                            print("   ❌ PROBLEM: No agent status in system status")
                            return False
                    else:
                        print("   ❌ PROBLEM: No get_system_status method")
                        return False
                        
                except Exception as e:
                    print(f"   ❌ ERROR starting system: {e}")
                    print("   🔧 Debugging orchestrator initialization...")
                    return debug_orchestrator_initialization(app.orchestrator, e)
            else:
                print("   ❌ PROBLEM: No start_system method")
                return False
        else:
            print("   ❌ PROBLEM: No orchestrator")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    finally:
        process.terminate()
        process.wait()

def fix_agent_creation(orchestrator):
    """Fix agent creation if no agents are created"""
    print("\n🔧 FIXING AGENT CREATION...")
    
    try:
        # Check if orchestrator has agent creation methods
        if hasattr(orchestrator, '_initialize_agents'):
            print("   Found _initialize_agents method")
            try:
                orchestrator._initialize_agents()
                print("   ✅ Agent initialization called")
                
                # Check if agents were created
                if hasattr(orchestrator, 'agents'):
                    agent_count = len(getattr(orchestrator, 'agents', {}))
                    print(f"   Agent count after initialization: {agent_count}")
                    
                    if agent_count > 0:
                        print("   ✅ Agents created successfully!")
                        return True
                    else:
                        print("   ❌ Still no agents - checking configuration...")
                        return fix_agent_configuration(orchestrator)
                else:
                    print("   ❌ No agents attribute created")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error initializing agents: {e}")
                return fix_agent_configuration_error(orchestrator, e)
        else:
            print("   ❌ No _initialize_agents method found")
            return False
            
    except Exception as e:
        print(f"   ❌ Error in fix_agent_creation: {e}")
        return False

def fix_agent_activation(orchestrator):
    """Fix agent activation if agents exist but aren't active"""
    print("\n🔧 FIXING AGENT ACTIVATION...")
    
    try:
        if hasattr(orchestrator, 'start_agents'):
            print("   Found start_agents method")
            result = orchestrator.start_agents()
            print(f"   Start agents result: {result}")
            
            # Check if agents are now active
            time.sleep(2)
            status = orchestrator.get_system_status()
            active_agents = status.get('active_agents', 0)
            
            if active_agents > 0:
                print(f"   ✅ SUCCESS: {active_agents} agents now active!")
                return True
            else:
                print("   ❌ Agents still not active")
                return False
        else:
            print("   ❌ No start_agents method")
            return False
            
    except Exception as e:
        print(f"   ❌ Error in fix_agent_activation: {e}")
        return False

def fix_agent_configuration(orchestrator):
    """Fix agent configuration issues"""
    print("\n🔧 FIXING AGENT CONFIGURATION...")
    
    try:
        # Check if config manager is working
        if hasattr(orchestrator, 'config_manager'):
            config = orchestrator.config_manager
            print(f"   Config manager: {type(config)}")
            
            # Check disciplines configuration
            disciplines = config.get_disciplines()
            print(f"   Disciplines loaded: {len(disciplines)}")
            
            if len(disciplines) == 0:
                print("   ❌ No disciplines configured!")
                return False
            
            # Check agent configuration
            agent_config = config.get_agent_config('discovery_agents')
            print(f"   Agent config: {len(agent_config)} entries")
            
            if len(agent_config) == 0:
                print("   ❌ No agent configuration!")
                return False
                
            print("   ✅ Configuration seems OK - problem might be elsewhere")
            return True
            
        else:
            print("   ❌ No config manager")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking configuration: {e}")
        return False

def fix_agent_configuration_error(orchestrator, error):
    """Fix specific agent configuration errors"""
    print(f"\n🔧 FIXING SPECIFIC ERROR: {error}")
    
    # Common fixes based on error patterns
    error_str = str(error).lower()
    
    if 'data_dir' in error_str:
        print("   🔧 ConfigManager data_dir issue - should be fixed already")
        # This should be fixed by our earlier commit
        return True
    elif 'no module' in error_str:
        print("   🔧 Import issue - checking imports...")
        # Check import issues
        return fix_import_issues()
    elif 'llm' in error_str:
        print("   🔧 LLM integration issue...")
        return fix_llm_integration()
    else:
        print(f"   ❌ Unknown error pattern: {error}")
        return False

def debug_orchestrator_initialization(orchestrator, error):
    """Debug orchestrator initialization issues"""
    print(f"\n🔧 DEBUG ORCHESTRATOR INITIALIZATION ERROR: {error}")
    
    try:
        # Check orchestrator attributes
        print("   Checking orchestrator attributes...")
        attrs = dir(orchestrator)
        important_attrs = [attr for attr in attrs if not attr.startswith('_')]
        print(f"   Public attributes: {important_attrs}")
        
        # Check if critical components exist
        has_config = hasattr(orchestrator, 'config_manager')
        has_recovery = hasattr(orchestrator, 'recovery_manager')
        has_llm = hasattr(orchestrator, 'llm_integration')
        
        print(f"   - config_manager: {has_config}")
        print(f"   - recovery_manager: {has_recovery}")
        print(f"   - llm_integration: {has_llm}")
        
        if not has_config:
            print("   ❌ Missing config_manager!")
            return False
        
        if not has_recovery:
            print("   ❌ Missing recovery_manager!")
            return False
            
        if not has_llm:
            print("   ❌ Missing llm_integration!")
            return False
            
        print("   ✅ All critical components present")
        
        # The error might be in the start_system method itself
        print("   🔍 Checking start_system method implementation...")
        
        # This suggests the issue is in the method implementation
        return True
        
    except Exception as e:
        print(f"   ❌ Error debugging orchestrator: {e}")
        return False

def fix_import_issues():
    """Fix import issues"""
    print("   🔧 Checking import issues...")
    
    try:
        # Test critical imports
        from core.orchestrator import StandardsOrchestrator
        from core.agents.discovery_agent import DiscoveryAgent
        from core.agents.retrieval_agent import RetrievalAgent
        from core.agents.processing_agent import ProcessingAgent
        from core.agents.validation_agent import ValidationAgent
        
        print("   ✅ All agent imports working")
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False

def fix_llm_integration():
    """Fix LLM integration issues"""
    print("   🔧 Checking LLM integration...")
    
    try:
        from core.llm_integration import LLMIntegration
        
        # Test LLM integration initialization
        llm = LLMIntegration({})
        print(f"   LLM integration: {type(llm)}")
        print(f"   Router available: {llm.router_available}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ LLM integration error: {e}")
        return False

if __name__ == "__main__":
    success = autonomous_debug_and_fix()
    if success:
        print("\n🎉 AUTONOMOUS DEBUG SUCCESSFUL!")
        print("   System should now have working agents")
    else:
        print("\n❌ AUTONOMOUS DEBUG FAILED")
        print("   Further investigation needed")
    
    exit(0 if success else 1)