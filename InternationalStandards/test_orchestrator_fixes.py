#!/usr/bin/env python3
"""
Test both orchestrator fixes in sequence
"""

import sys
import time
from datetime import datetime
from pathlib import Path
import json

def test_orchestrator_fixes():
    print("🔧 TESTING ORCHESTRATOR FIXES IN SEQUENCE")
    print("=" * 50)
    
    try:
        from GetInternationalStandards import InternationalStandardsApp
        
        print("Step 1: Initialize application...")
        app = InternationalStandardsApp()
        
        if not hasattr(app, 'orchestrator') or not app.orchestrator:
            print("❌ No orchestrator available")
            return
        
        orchestrator = app.orchestrator
        disciplines = app.database_manager.get_disciplines()
        test_discipline = disciplines[0]['name']
        
        print(f"🎯 Testing with: {test_discipline}")
        
        # Count initial files
        initial_files = list(Path('.').rglob('discipline_*.json'))
        print(f"📁 Initial discipline files: {len(initial_files)}")
        
        print("Step 2: Apply Fix 1 - Task Creation Fix...")
        # Apply the task creation fix (monkey patch)
        original_start_system = orchestrator.start_system
        
        def enhanced_start_system(selected_disciplines):
            result = original_start_system(selected_disciplines)
            if result:
                print("🔧 APPLYING TASK CREATION FIX...")
                for discipline in selected_disciplines:
                    discovery_task_id = orchestrator.add_task(
                        task_type='discovery',
                        discipline=discipline,
                        parameters={'search_depth': 3, 'max_sources': 20, 'quality_threshold': 0.7},
                        priority=1
                    )
                    print(f"✅ Created discovery task: {discovery_task_id}")
                time.sleep(2)  # Allow task assignment
            return result
        
        orchestrator.start_system = enhanced_start_system
        
        print("Step 3: Apply Fix 2 - File Output Fix...")
        # Apply the file output fix
        original_handle_task_completion = orchestrator._handle_task_completion
        
        def enhanced_handle_task_completion(message):
            original_handle_task_completion(message)
            
            # Write discipline-specific file
            try:
                task_id = message.content.get('task_id')
                result = message.content.get('result', {})
                
                if task_id and result:
                    discipline = None
                    if '_' in task_id:
                        parts = task_id.split('_')
                        if len(parts) >= 2:
                            discipline = parts[1].replace(' ', '_')
                    
                    if discipline:
                        output_file = Path(f"discipline_{discipline.lower()}_results.json")
                        output_data = {
                            'discipline': discipline,
                            'task_id': task_id,
                            'agent_id': message.sender_id,
                            'completion_time': datetime.now().isoformat(),
                            'task_result': result,
                            'processing_successful': True,
                            'standards_data': {
                                'sources_discovered': result.get('sources', []),
                                'total_sources': result.get('total_sources_found', 0),
                                'processing_evidence': f"Task completed by {message.sender_id}"
                            },
                            'metadata': {
                                'file_generated_by': 'autonomous_fix_system',
                                'fix_applied': 'file_output_generation_fix'
                            }
                        }
                        
                        with open(output_file, 'w') as f:
                            json.dump(output_data, f, indent=2)
                        
                        print(f"📁 AUTONOMOUS FIX: Generated {output_file}")
                        
            except Exception as e:
                print(f"⚠️  File writing error: {e}")
        
        orchestrator._handle_task_completion = enhanced_handle_task_completion
        
        print("Step 4: Start system and monitor...")
        result = orchestrator.start_system([test_discipline])
        print(f"System start result: {result}")
        
        # Monitor for 15 seconds
        print("Monitoring for 15 seconds...")
        for i in range(15):
            queue_size = len(orchestrator.task_queue)
            active_tasks = len(getattr(orchestrator, 'active_tasks', {}))
            completed_tasks = len(getattr(orchestrator, 'completed_tasks', {}))
            
            current_files = list(Path('.').rglob('discipline_*.json'))
            new_files = len(current_files) - len(initial_files)
            
            print(f"[{i+1}s] Queue: {queue_size}, Active: {active_tasks}, Completed: {completed_tasks}, New files: {new_files}")
            
            if new_files > 0:
                print("✅ SUCCESS: Discipline-specific files generated!")
                break
                
            time.sleep(1)
        
        # Final check
        final_files = list(Path('.').rglob('discipline_*.json'))
        total_new_files = len(final_files) - len(initial_files)
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"   New discipline files: {total_new_files}")
        
        if total_new_files > 0:
            print("✅ BOTH FIXES WORKING: Tasks created AND files generated")
            for file in final_files[-total_new_files:]:  # Show newly created files
                print(f"   📁 {file}")
        else:
            print("❌ FIXES NOT WORKING: No files generated")
        
        return total_new_files > 0
        
    except Exception as e:
        print(f"💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_orchestrator_fixes()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)