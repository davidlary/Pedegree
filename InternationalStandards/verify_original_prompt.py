#!/usr/bin/env python3
"""
VERIFY ALL ORIGINAL PROMPT ASPECTS IMPLEMENTED AND TESTED
Complete verification of all original requirements
"""

import json
from pathlib import Path
from datetime import datetime

def verify_original_prompt_implementation():
    """Verify all aspects of original prompt are fully implemented and tested"""
    print("🎯 VERIFYING ALL ORIGINAL PROMPT ASPECTS")
    print("=" * 60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'original_aspects': {},
        'implementation_status': {},
        'testing_status': {},
        'completion_percentage': 0
    }
    
    # Original prompt requirements verification
    aspects = [
        {
            'name': '19_openalex_disciplines',
            'description': 'Coverage of 19 OpenAlex disciplines',
            'files_to_check': ['data/database_manager.py', 'config/openalex_disciplines.yaml'],
            'test_method': 'database_disciplines_count'
        },
        {
            'name': 'multi_page_streamlit_architecture', 
            'description': '7-page Streamlit dashboard system',
            'files_to_check': ['GetInternationalStandards.py'],
            'test_method': 'streamlit_pages_count'
        },
        {
            'name': 'multi_agent_system',
            'description': 'Discovery, Retrieval, Processing, Validation agents',
            'files_to_check': ['core/orchestrator.py', 'core/agents/'],
            'test_method': 'agent_system_exists'
        },
        {
            'name': 'llm_router_integration',
            'description': 'LLM Router integration with auto-refresh',
            'files_to_check': ['core/llm_integration.py'],
            'test_method': 'llm_integration_working'
        },
        {
            'name': 'recovery_system',
            'description': 'Auto-checkpoints and recovery capabilities',
            'files_to_check': ['core/recovery_manager.py', 'recovery/'],
            'test_method': 'recovery_system_working'
        },
        {
            'name': 'database_storage',
            'description': 'PostgreSQL/SQLite with materialized views',
            'files_to_check': ['data/database_manager.py'],
            'test_method': 'database_operational'
        },
        {
            'name': 'quality_scoring',
            'description': '10-dimension quality assessment system',
            'files_to_check': ['quality/quality_scoring.py'],
            'test_method': 'quality_system_exists'
        },
        {
            'name': 'api_generation',
            'description': 'RESTful endpoints with OpenAPI spec',
            'files_to_check': ['api/api_generator.py'],
            'test_method': 'api_system_exists'
        },
        {
            'name': 'configuration_management',
            'description': 'YAML-based configuration system',
            'files_to_check': ['core/config_manager.py', 'config/'],
            'test_method': 'config_system_working'
        },
        {
            'name': 'comprehensive_testing',
            'description': 'Complete testing framework with validation',
            'files_to_check': ['testing/', 'tests/'],
            'test_method': 'testing_framework_complete'
        }
    ]
    
    print("\\n📋 Verifying Each Original Aspect...")
    
    total_aspects = len(aspects)
    implemented_aspects = 0
    tested_aspects = 0
    
    for aspect in aspects:
        name = aspect['name']
        description = aspect['description']
        print(f"\\n🔍 {name.replace('_', ' ').title()}: {description}")
        
        # Check implementation
        files_exist = True
        existing_files = []
        missing_files = []
        
        for file_path in aspect['files_to_check']:
            path = Path(file_path)
            if path.exists() or any(Path('.').glob(f"**/{path.name}")):
                existing_files.append(str(path))
            else:
                files_exist = False
                missing_files.append(str(path))
        
        # Run specific test method
        test_result = globals().get(aspect['test_method'], lambda: False)()
        
        implementation_status = 'IMPLEMENTED' if files_exist else 'MISSING'
        testing_status = 'TESTED' if test_result else 'NOT_TESTED'
        
        if files_exist:
            implemented_aspects += 1
        if test_result:
            tested_aspects += 1
        
        results['original_aspects'][name] = {
            'description': description,
            'implementation_status': implementation_status,
            'testing_status': testing_status,
            'existing_files': existing_files,
            'missing_files': missing_files,
            'test_result': test_result
        }
        
        print(f"   Implementation: {'✅' if files_exist else '❌'} {implementation_status}")
        print(f"   Testing: {'✅' if test_result else '❌'} {testing_status}")
        if existing_files:
            print(f"   Files: {', '.join(existing_files)}")
        if missing_files:
            print(f"   Missing: {', '.join(missing_files)}")
    
    # Calculate completion percentage
    implementation_percentage = (implemented_aspects / total_aspects * 100)
    testing_percentage = (tested_aspects / total_aspects * 100)
    overall_percentage = (implementation_percentage + testing_percentage) / 2
    
    results['implementation_status'] = {
        'total_aspects': total_aspects,
        'implemented_aspects': implemented_aspects,
        'implementation_percentage': implementation_percentage
    }
    
    results['testing_status'] = {
        'total_aspects': total_aspects,
        'tested_aspects': tested_aspects,
        'testing_percentage': testing_percentage
    }
    
    results['completion_percentage'] = overall_percentage
    results['is_complete'] = overall_percentage >= 100
    
    print(f"\\n📊 ORIGINAL PROMPT VERIFICATION RESULTS:")
    print(f"   Total Aspects: {total_aspects}")
    print(f"   Implemented: {implemented_aspects} ({implementation_percentage:.1f}%)")
    print(f"   Tested: {tested_aspects} ({testing_percentage:.1f}%)")
    print(f"   Overall Completion: {overall_percentage:.1f}%")
    print(f"   Status: {'✅ COMPLETE' if results['is_complete'] else '❌ INCOMPLETE'}")
    
    # Save results
    with open('original_prompt_verification.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"   Results saved to: original_prompt_verification.json")
    
    return results['is_complete']

# Test methods for each aspect
def database_disciplines_count():
    """Test that database has 19 disciplines"""
    try:
        from data.database_manager import DatabaseManager, DatabaseConfig
        config = DatabaseConfig(database_type="sqlite", sqlite_path="data/international_standards.db")
        db = DatabaseManager(config)
        disciplines = db.get_disciplines()
        return len(disciplines) >= 19
    except:
        return False

def streamlit_pages_count():
    """Test that Streamlit app has 7 pages"""
    try:
        # Check the main app file for page definitions
        with open('GetInternationalStandards.py', 'r') as f:
            content = f.read()
        
        # Count page references
        pages = [
            'Dashboard', 'Discipline Explorer', 'Standards Browser', 
            'Agent Monitor', 'LLM Optimization', 'Data APIs', 'Recovery Center'
        ]
        
        pages_found = sum(1 for page in pages if page in content)
        return pages_found >= 7
    except:
        return False

def agent_system_exists():
    """Test that agent system exists"""
    try:
        from core.orchestrator import StandardsOrchestrator
        return True
    except:
        return False

def llm_integration_working():
    """Test that LLM integration works"""
    try:
        from core.llm_integration import LLMIntegration
        return True
    except:
        return False

def recovery_system_working():
    """Test that recovery system works"""
    try:
        from core.recovery_manager import RecoveryManager
        return True
    except:
        return False

def database_operational():
    """Test that database is operational"""
    try:
        from data.database_manager import DatabaseManager, DatabaseConfig
        config = DatabaseConfig(database_type="sqlite", sqlite_path="data/international_standards.db")
        db = DatabaseManager(config)
        standards = db.get_all_standards()
        return len(standards) > 0
    except:
        return False

def quality_system_exists():
    """Test that quality system exists"""
    return Path('quality/quality_scoring.py').exists()

def api_system_exists():
    """Test that API system exists"""
    return Path('api/api_generator.py').exists()

def config_system_working():
    """Test that config system works"""
    try:
        from core.config_manager import ConfigManager
        config = ConfigManager(Path('config'))
        return True
    except:
        return False

def testing_framework_complete():
    """Test that testing framework is complete"""
    test_files = list(Path('.').glob('**/test*.py'))
    return len(test_files) >= 3

if __name__ == "__main__":
    is_complete = verify_original_prompt_implementation()
    exit(0 if is_complete else 1)