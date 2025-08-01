#!/usr/bin/env python3
"""
FIX AGENT STARTUP - Debug and fix the specific agent startup issue
"""

def test_agent_startup():
    """Test the actual agent startup process"""
    print("🔧 TESTING AGENT STARTUP PROCESS")
    print("=" * 50)
    
    try:
        from GetInternationalStandards import InternationalStandardsApp
        
        app = InternationalStandardsApp()
        print(f"✅ App initialized: {bool(app)}")
        print(f"✅ Orchestrator exists: {bool(app.orchestrator)}")
        
        if app.orchestrator:
            # Test with all disciplines like the app does
            all_disciplines = [
                "Physical_Sciences", "Life_Sciences", "Health_Sciences", "Social_Sciences",
                "Computer_Science", "Mathematics", "Engineering", "Business", "Economics",
                "Geography", "Environmental_Science", "Earth_Sciences", "Agricultural_Sciences",
                "History", "Philosophy", "Art", "Literature", "Education", "Law"
            ]
            
            print(f"Testing start_system with {len(all_disciplines)} disciplines...")
            
            try:
                result = app.orchestrator.start_system(all_disciplines)
                print(f"✅ start_system result: {result}")
                
                # Wait for agents to initialize
                import time
                time.sleep(3)
                
                # Check system status
                status = app.orchestrator.get_system_status()
                print(f"System running: {status.get('is_running', False)}")
                
                # Get active agent count from system_metrics
                system_metrics = status.get('system_metrics', {})
                active_agents = system_metrics.get('total_agents_active', 0)
                print(f"Active agents: {active_agents}")
                
                if active_agents > 0:
                    print(f"🎉 SUCCESS! {active_agents} agents are now running!")
                    
                    # Test getting agent details
                    agent_details = app.orchestrator.get_agent_status()
                    print(f"Agent details: {len(agent_details)} agents")
                    
                    for agent_id, details in list(agent_details.items())[:5]:  # Show first 5
                        print(f"  {agent_id}: {details.get('status', 'unknown')}")
                    
                    return True
                else:
                    print("❌ PROBLEM: Agents started but not showing as active")
                    
                    # Debug agent creation
                    if hasattr(app.orchestrator, 'agents'):
                        agents = app.orchestrator.agents
                        print(f"Agent dict has {len(agents)} entries")
                        
                        for agent_id, agent in list(agents.items())[:3]:
                            print(f"  Agent {agent_id}: {type(agent)}")
                            if hasattr(agent, 'status'):
                                print(f"    Status: {agent.status}")
                            if hasattr(agent, 'is_active'):
                                print(f"    Active: {agent.is_active}")
                    
                    return False
                    
            except Exception as e:
                print(f"❌ ERROR in start_system: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("❌ No orchestrator available")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agent_startup()
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}: Agent startup test")
    exit(0 if success else 1)