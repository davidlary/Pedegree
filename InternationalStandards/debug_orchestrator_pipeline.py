#!/usr/bin/env python3
"""
DEBUG ORCHESTRATOR PROCESSING PIPELINE
Deep investigation of why tasks aren't being processed
"""

import sys
import time
from datetime import datetime
from pathlib import Path
import json

def debug_orchestrator_pipeline():
    print("🔍 DEBUGGING ORCHESTRATOR PROCESSING PIPELINE")
    print("=" * 60)
    
    try:
        from GetInternationalStandards import InternationalStandardsApp
        
        print("Step 1: Initialize application...")
        app = InternationalStandardsApp()
        
        print("Step 2: Check orchestrator availability...")
        if not hasattr(app, 'orchestrator') or not app.orchestrator:
            print("❌ CRITICAL: No orchestrator available")
            return
        
        orchestrator = app.orchestrator
        print(f"✅ Orchestrator available: {type(orchestrator)}")
        
        print("Step 3: Get disciplines...")
        disciplines = app.database_manager.get_disciplines()
        print(f"✅ Found {len(disciplines)} disciplines")
        
        # Use first discipline for testing
        test_discipline = disciplines[0]['name']
        print(f"🎯 Testing with discipline: {test_discipline}")
        
        print("Step 4: Check initial orchestrator state...")
        initial_agent_count = len(orchestrator.agents)
        initial_task_queue_size = len(orchestrator.task_queue)
        initial_active_tasks = len(getattr(orchestrator, 'active_tasks', {}))
        
        print(f"📊 Initial state:")
        print(f"   - Agents: {initial_agent_count}")
        print(f"   - Task queue: {initial_task_queue_size}")
        print(f"   - Active tasks: {initial_active_tasks}")
        print(f"   - Is running: {orchestrator.is_running}")
        
        print("Step 5: Start system...")
        result = orchestrator.start_system([test_discipline])
        print(f"✅ System start result: {result}")
        
        print("Step 6: Check state after system start...")
        post_start_agent_count = len(orchestrator.agents)
        post_start_task_queue_size = len(orchestrator.task_queue)
        post_start_active_tasks = len(getattr(orchestrator, 'active_tasks', {}))
        
        print(f"📊 Post-start state:")
        print(f"   - Agents: {post_start_agent_count}")
        print(f"   - Task queue: {post_start_task_queue_size}")
        print(f"   - Active tasks: {post_start_active_tasks}")
        print(f"   - Is running: {orchestrator.is_running}")
        
        # Check agent status
        agent_status = orchestrator.get_agent_status()
        print(f"📊 Agent status ({len(agent_status)} agents):")
        for agent_id, status in list(agent_status.items())[:5]:  # Show first 5
            print(f"   - {agent_id}: {status.get('status', 'unknown')}")
        
        print("Step 7: Manually create tasks (simulating the fix)...")
        
        # Create discovery task
        discovery_task_id = orchestrator.add_task(
            task_type='discovery',
            discipline=test_discipline,
            parameters={
                'search_depth': 3,
                'max_sources': 20,
                'quality_threshold': 0.7
            },
            priority=1
        )
        
        # Create processing task  
        processing_task_id = orchestrator.add_task(
            task_type='processing',
            discipline=test_discipline,
            parameters={
                'process_discovered_sources': True,
                'output_format': 'json'
            },
            priority=2
        )
        
        print(f"✅ Created tasks:")
        print(f"   - Discovery: {discovery_task_id}")
        print(f"   - Processing: {processing_task_id}")
        
        print("Step 8: Check state after task creation...")
        post_task_queue_size = len(orchestrator.task_queue)
        post_task_active_tasks = len(getattr(orchestrator, 'active_tasks', {}))
        
        print(f"📊 Post-task-creation state:")
        print(f"   - Task queue: {post_task_queue_size}")
        print(f"   - Active tasks: {post_task_active_tasks}")
        
        print("Step 9: Monitor task processing for 30 seconds...")
        monitoring_start = time.time()
        
        while time.time() - monitoring_start < 30:
            current_queue_size = len(orchestrator.task_queue)
            current_active_tasks = len(getattr(orchestrator, 'active_tasks', {}))
            current_completed_tasks = len(getattr(orchestrator, 'completed_tasks', {}))
            
            # Check agent statuses
            agent_status = orchestrator.get_agent_status()
            running_agents = sum(1 for status in agent_status.values() 
                               if status.get('status') == 'running')
            idle_agents = sum(1 for status in agent_status.values() 
                            if status.get('status') == 'idle')
            
            elapsed = time.time() - monitoring_start
            print(f"⏱️  [{elapsed:.1f}s] Queue: {current_queue_size}, Active: {current_active_tasks}, "
                  f"Completed: {current_completed_tasks}, Running agents: {running_agents}, Idle: {idle_agents}")
            
            # Check if tasks moved from queue to active
            if current_queue_size < post_task_queue_size:
                print(f"✅ Tasks moved from queue to active processing!")
                
            # Check if any tasks completed
            if current_completed_tasks > 0:
                print(f"✅ Tasks completed! ({current_completed_tasks})")
                break
                
            time.sleep(2)
        
        print("Step 10: Final state analysis...")
        final_queue_size = len(orchestrator.task_queue)
        final_active_tasks = len(getattr(orchestrator, 'active_tasks', {}))
        final_completed_tasks = len(getattr(orchestrator, 'completed_tasks', {}))
        
        print(f"📊 Final state:")
        print(f"   - Task queue: {final_queue_size}")
        print(f"   - Active tasks: {final_active_tasks}")
        print(f"   - Completed tasks: {final_completed_tasks}")
        
        # Check for output files
        print("Step 11: Check for output files...")
        output_files = list(Path('.').rglob('*.json')) + list(Path('.').rglob('*.csv'))
        discipline_files = [f for f in output_files if test_discipline.lower().replace(' ', '_') in str(f).lower()]
        
        print(f"📁 Output files found: {len(output_files)} total, {len(discipline_files)} discipline-specific")
        
        # ROOT CAUSE ANALYSIS
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        print("=" * 40)
        
        if final_queue_size == post_task_queue_size and final_active_tasks == 0:
            print("❌ PROBLEM: Tasks created but never moved to active processing")
            print("   - Possible cause: Task assignment mechanism not working")
            print("   - Check: _process_task_queue() not being called or failing")
            
        elif final_active_tasks > 0 and final_completed_tasks == 0:
            print("❌ PROBLEM: Tasks assigned to agents but never completing")
            print("   - Possible cause: Agents receiving tasks but not processing them")
            print("   - Check: Agent _process_task() method or main loop issues")
            
        elif final_completed_tasks > 0 and len(discipline_files) == 0:
            print("❌ PROBLEM: Tasks completing but no output files generated")
            print("   - Possible cause: Task processing succeeds but doesn't write files")
            print("   - Check: File writing logic in agent task processing")
            
        elif len(discipline_files) > 0:
            print("✅ SUCCESS: Tasks processed and files generated!")
        else:
            print("❌ UNKNOWN PROBLEM: Investigate orchestrator and agent interaction")
        
        # Additional debugging info
        print(f"\n🔍 ADDITIONAL DEBUG INFO:")
        print(f"   - Orchestrator main loop running: {orchestrator.is_running}")
        print(f"   - Orchestrator thread alive: {orchestrator.orchestrator_thread.is_alive() if orchestrator.orchestrator_thread else False}")
        
        # Check one agent in detail
        if orchestrator.agents:
            first_agent_id = list(orchestrator.agents.keys())[0]
            first_agent = orchestrator.agents[first_agent_id]
            agent_detailed_status = first_agent.get_status()
            print(f"   - Sample agent ({first_agent_id}):")
            print(f"     * Status: {agent_detailed_status.get('status')}")
            print(f"     * Current task: {agent_detailed_status.get('current_task')}")
            print(f"     * Task queue size: {agent_detailed_status.get('task_queue_size')}")
        
    except Exception as e:
        print(f"💥 DEBUG FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_orchestrator_pipeline()