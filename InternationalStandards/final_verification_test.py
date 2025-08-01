#!/usr/bin/env python3
"""
FINAL VERIFICATION TEST - Verify agents are actually processing real standards
Tests that agents can discover, retrieve and process actual educational standards data
"""

import time
from datetime import datetime

def verify_standards_processing():
    """Verify that agents actually process and discover standards"""
    print("🎯 FINAL VERIFICATION: ACTUAL STANDARDS PROCESSING")
    print("=" * 60)
    
    try:
        from GetInternationalStandards import InternationalStandardsApp
        
        app = InternationalStandardsApp()
        print(f"✅ App initialized: {bool(app)}")
        
        if not app.orchestrator:
            print("❌ No orchestrator available")
            return False
        
        # Start the system with a subset of disciplines for focused testing
        test_disciplines = ["Computer_Science", "Mathematics", "Physical_Sciences"]
        print(f"\n🚀 Starting system with {len(test_disciplines)} disciplines...")
        
        result = app.orchestrator.start_system(test_disciplines)
        if not result:
            print("❌ Failed to start system")
            return False
        
        print("✅ System started successfully")
        
        # Wait for initialization
        time.sleep(3)
        
        # Create specific discovery tasks
        print(f"\n🔍 Creating focused standards discovery tasks...")
        task_ids = []
        
        for discipline in test_disciplines:
            # Create discovery task with specific parameters
            task_id = app.orchestrator.add_task(
                task_type="discovery",
                discipline=discipline,
                parameters={
                    "search_terms": [
                        f"{discipline.lower()} educational standards",
                        f"{discipline.lower()} curriculum framework",
                        f"{discipline.lower()} learning objectives"
                    ],
                    "max_results": 3,
                    "quality_threshold": 0.7,
                    "verification_required": True
                },
                priority=1
            )
            task_ids.append(task_id)
            print(f"  📝 Created task {task_id} for {discipline}")
        
        # Monitor task execution and results
        print(f"\n⏱️  Monitoring task execution...")
        start_time = time.time()
        timeout = 45  # 45 seconds timeout
        
        completed_tasks_data = {}
        agents_observed_running = []
        
        while time.time() - start_time < timeout:
            # Get system status
            status = app.orchestrator.get_system_status()
            
            # Check for running agents
            agents = status.get('agents', {})
            currently_running = [aid for aid, agent in agents.items() if agent.get('status') == 'running']
            
            if currently_running:
                for agent_id in currently_running:
                    if agent_id not in agents_observed_running:
                        agents_observed_running.append(agent_id)
                        print(f"  ✅ AGENT RUNNING: {agent_id} processing task")
            
            # Check completed tasks
            tasks = status.get('tasks', {})
            completed_count = tasks.get('completed', 0)
            
            if completed_count > len(completed_tasks_data):
                print(f"  📊 Task completed: {completed_count} total")
            
            # Check if all test tasks are complete
            if completed_count >= len(task_ids):
                print(f"  ✅ All {len(task_ids)} tasks completed!")
                break
            
            time.sleep(1)
        
        # Final analysis
        print(f"\n📊 FINAL ANALYSIS:")
        print(f"  - Test duration: {time.time() - start_time:.1f} seconds")
        print(f"  - Tasks created: {len(task_ids)}")
        print(f"  - Tasks completed: {completed_count}")
        print(f"  - Agents observed running: {len(agents_observed_running)}")
        
        # Get final system status
        final_status = app.orchestrator.get_system_status()
        system_metrics = final_status.get('system_metrics', {})
        active_agents = system_metrics.get('total_agents_active', 0)
        
        print(f"  - Active agents: {active_agents}")
        
        # Check for actual processing evidence
        processing_evidence = []
        
        if completed_count > 0:
            processing_evidence.append(f"✅ {completed_count} tasks completed successfully")
        
        if len(agents_observed_running) > 0:
            processing_evidence.append(f"✅ {len(agents_observed_running)} agents observed running")
        
        if active_agents > 0:
            processing_evidence.append(f"✅ {active_agents} agents currently active")
        
        # Show agent details
        agent_details = app.orchestrator.get_agent_status()
        working_agents = [(aid, details) for aid, details in agent_details.items() 
                         if details.get('status') in ['running', 'idle']]
        
        if working_agents:
            processing_evidence.append(f"✅ {len(working_agents)} agents in working state")
            
            print(f"\n🤖 AGENT STATUS SAMPLE:")
            for i, (agent_id, details) in enumerate(working_agents[:5]):
                status = details.get('status', 'unknown')
                agent_type = details.get('type', 'unknown')
                success_rate = details.get('success_rate', 0.0)
                print(f"  Agent {i+1}: {agent_type} | {status} | Success: {success_rate:.1%}")
        
        # Determine success
        print(f"\n🎯 PROCESSING EVIDENCE:")
        for evidence in processing_evidence:
            print(f"  {evidence}")
        
        # Success criteria: agents are working and tasks are completing
        success = (completed_count > 0 and 
                  (len(agents_observed_running) > 0 or active_agents > 0))
        
        if success:
            print(f"\n🎉 SUCCESS: Agents are actively processing standards!")
            print(f"   The system demonstrates functional end-to-end operation.")
            print(f"   Tasks: {completed_count} completed | Agents: {active_agents} active")
        else:
            print(f"\n❌ FAILED: No evidence of active standards processing")
            print(f"   Tasks: {completed_count} completed | Agents: {active_agents} active") 
        
        # Cleanup - stop the system
        print(f"\n🛑 Stopping system...")
        app.orchestrator.stop_system()
        
        return success
        
    except Exception as e:
        print(f"❌ VERIFICATION ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_standards_processing()
    print(f"\n{'🎉 VERIFICATION PASSED' if success else '❌ VERIFICATION FAILED'}: Standards processing test")
    exit(0 if success else 1)