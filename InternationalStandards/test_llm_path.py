#!/usr/bin/env python3
"""
Test LLM Router path resolution
"""

from pathlib import Path

def test_path_resolution():
    """Test the LLM Router path resolution"""
    print("🔍 Testing LLM Router Path Resolution...")
    
    # Same logic as in GetInternationalStandards.py
    project_root = Path(__file__).parent
    llm_comparisons_path = project_root.parent / "LLM-Comparisons"
    models_path = llm_comparisons_path / "available_models_current.json"
    
    print(f"  project_root: {project_root}")
    print(f"  llm_comparisons_path: {llm_comparisons_path}")
    print(f"  models_path: {models_path}")
    print(f"  models_path exists: {models_path.exists()}")
    
    if models_path.exists():
        print(f"  File size: {models_path.stat().st_size} bytes")
        print("  ✅ Path resolution working correctly!")
        
        # Test reading the file
        try:
            import json
            with open(models_path, 'r') as f:
                data = json.load(f)
            print(f"  ✅ JSON file readable, contains {len(data)} entries")
        except Exception as e:
            print(f"  ❌ Error reading JSON: {e}")
    else:
        print("  ❌ Path resolution failed!")
    
    # Test the new path in orchestrator initialization
    orchestrator_models_path = str(Path(__file__).parent.parent / "LLM-Comparisons" / "available_models_current.json")
    print(f"  orchestrator_models_path: {orchestrator_models_path}")
    print(f"  orchestrator path exists: {Path(orchestrator_models_path).exists()}")

if __name__ == "__main__":
    test_path_resolution()