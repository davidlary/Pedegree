#!/usr/bin/env python3
"""Debug discipline loading"""

import yaml
from pathlib import Path

def debug_discipline_loading():
    print("🔍 DEBUGGING DISCIPLINE LOADING")
    print("=" * 50)
    
    # Check config file path
    config_dir = Path(__file__).parent / "config"
    openalex_config_path = config_dir / "openalex_disciplines.yaml"
    
    print(f"📁 Config directory: {config_dir}")
    print(f"📄 Config file path: {openalex_config_path}")
    print(f"✅ File exists: {openalex_config_path.exists()}")
    
    if openalex_config_path.exists():
        print(f"\n📖 Reading config file...")
        with open(openalex_config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        disciplines = config.get('disciplines', {})
        print(f"📊 Found {len(disciplines)} disciplines in config")
        
        print(f"\n🏷️  First 5 disciplines:")
        for i, (key, info) in enumerate(list(disciplines.items())[:5]):
            display_name = info.get('display_name', key.replace('_', ' '))
            print(f"   {i+1}. Key: {key}")
            print(f"      Display Name: {display_name}")
            print(f"      Description: {info.get('description', 'N/A')}")
            print()
        
        # Test the formatting logic
        print(f"\n🔧 Testing formatting logic:")
        formatted_disciplines = []
        for i, (key, info) in enumerate(disciplines.items()):
            discipline = {
                'id': i + 1,
                'name': info.get('display_name', key.replace('_', ' ')),
                'key': key,
                'display_name': info.get('display_name', key.replace('_', ' ')),
                'description': info.get('description', ''),
                'subdisciplines': info.get('subdisciplines', []),
                'priority': info.get('priority', i + 1)
            }
            formatted_disciplines.append(discipline)
        
        print(f"📈 Formatted {len(formatted_disciplines)} disciplines")
        print(f"\n📋 First 3 formatted disciplines:")
        for disc in formatted_disciplines[:3]:
            print(f"   ID: {disc['id']}, Name: {disc['name']}, Key: {disc['key']}")
    
    else:
        print("❌ Config file not found!")

if __name__ == "__main__":
    debug_discipline_loading()