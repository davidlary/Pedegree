#!/usr/bin/env python3
"""
TERMINATE ALL AGENTS - Clean shutdown of all running agents
"""

def terminate_all_agents():
    """Cleanly terminate all running agents"""
    print("🛑 TERMINATING ALL AGENTS")
    print("=" * 50)
    
    try:
        from GetInternationalStandards import InternationalStandardsApp
        
        app = InternationalStandardsApp()
        print(f"✅ App initialized: {bool(app)}")
        
        if app.orchestrator:
            # Check current status
            status = app.orchestrator.get_system_status()
            is_running = status.get('is_running', False)
            system_metrics = status.get('system_metrics', {})
            active_agents = system_metrics.get('total_agents_active', 0)
            
            print(f"System running: {is_running}")
            print(f"Active agents before shutdown: {active_agents}")
            
            if is_running:
                print("Stopping orchestrator system...")
                result = app.orchestrator.stop_system()
                print(f"✅ System stopped: {result}")
                
                # Wait for clean shutdown
                import time
                time.sleep(2)
                
                # Verify shutdown
                status = app.orchestrator.get_system_status()
                is_running = status.get('is_running', False)
                system_metrics = status.get('system_metrics', {})
                active_agents = system_metrics.get('total_agents_active', 0)
                
                print(f"System running after shutdown: {is_running}")
                print(f"Active agents after shutdown: {active_agents}")
                
                if not is_running and active_agents == 0:
                    print("🎉 SUCCESS: All agents terminated cleanly")
                    return True
                else:
                    print(f"⚠️  WARNING: System may not have shut down completely")
                    return False
            else:
                print("✅ System was not running - no agents to terminate")
                return True
        else:
            print("❌ No orchestrator available")
            return False
            
    except Exception as e:
        print(f"❌ ERROR terminating agents: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = terminate_all_agents()
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}: Agent termination")
    exit(0 if success else 1)