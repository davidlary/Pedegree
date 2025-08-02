#!/usr/bin/env python3
"""Debug YAML loading issue"""

import yaml
from pathlib import Path

# Test YAML loading directly
config_dir = Path(__file__).parent / "config"
openalex_config_path = config_dir / "openalex_disciplines.yaml"

print("🔍 DEBUGGING YAML LOADING")
print(f"File path: {openalex_config_path}")
print(f"File exists: {openalex_config_path.exists()}")

if openalex_config_path.exists():
    with open(openalex_config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"Config loaded: {type(config)}")
    print(f"Keys: {list(config.keys())}")
    
    disciplines = config.get('disciplines', {})
    print(f"Disciplines: {len(disciplines)}")
    
    # Check first discipline
    first_key = list(disciplines.keys())[0]
    first_disc = disciplines[first_key]
    print(f"First discipline key: {first_key}")
    print(f"First discipline data: {first_disc}")
    print(f"Display name: {first_disc.get('display_name')}")
    
    # Test the exact logic from the app
    formatted_disciplines = []
    for i, (key, info) in enumerate(disciplines.items()):
        print(f"\nProcessing {key}:")
        print(f"  info type: {type(info)}")
        print(f"  info keys: {list(info.keys()) if isinstance(info, dict) else 'Not a dict'}")
        print(f"  display_name: {info.get('display_name') if isinstance(info, dict) else 'N/A'}")
        
        discipline = {
            'id': i + 1,
            'name': info.get('display_name', key.replace('_', ' ')) if isinstance(info, dict) else key.replace('_', ' '),
            'key': key,
            'display_name': info.get('display_name', key.replace('_', ' ')) if isinstance(info, dict) else key.replace('_', ' '),
            'description': info.get('description', '') if isinstance(info, dict) else '',
            'subdisciplines': info.get('subdisciplines', []) if isinstance(info, dict) else [],
            'priority': info.get('priority', i + 1) if isinstance(info, dict) else i + 1
        }
        formatted_disciplines.append(discipline)
        
        if i < 3:  # Only show first 3
            print(f"  Formatted: {discipline}")
        
        if i >= 2:  # Only process first 3
            break
    
    print(f"\nResult: {len(formatted_disciplines)} disciplines formatted")