#!/usr/bin/env python3
"""
Debug Test Runner for International Standards Retrieval System
Simple test execution without complex framework issues
"""

import sys
import traceback
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_core_imports():
    """Test all core module imports"""
    print("🔍 Testing Core Module Imports...")
    results = []
    
    test_modules = [
        ('GetInternationalStandards', 'InternationalStandardsApp'),
        ('core.orchestrator', 'StandardsOrchestrator'),
        ('core.llm_integration', 'LLMIntegration'),
        ('core.agents.base_agent', 'BaseAgent'),
        ('core.recovery_manager', 'RecoveryManager'),
        ('core.config_manager', 'ConfigManager'),
        ('data.database_manager', 'DatabaseManager'),
        ('quality.quality_scoring', 'QualityScoringEngine'),
        ('api.api_generator', 'APIGenerator'),
        ('data.data_integration', 'DataIntegrationManager'),
    ]
    
    for module_name, class_name in test_modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            results.append(f"✅ {module_name}.{class_name}")
        except Exception as e:
            results.append(f"❌ {module_name}.{class_name}: {str(e)[:100]}")
    
    return results

def test_configuration_files():
    """Test configuration file accessibility"""
    print("🔍 Testing Configuration Files...")
    results = []
    
    config_files = [
        'config/openalex_disciplines.yaml',
        'config/standards_ecosystem.yaml',
        'config/recovery_system.yaml',
        'config/llm_optimization.yaml',
        'config/system_architecture.yaml'
    ]
    
    for config_file in config_files:
        if Path(config_file).exists():
            if Path(config_file).stat().st_size > 0:
                results.append(f"✅ {config_file} (populated)")
            else:
                results.append(f"⚠️  {config_file} (empty)")
        else:
            results.append(f"❌ {config_file} (missing)")
    
    return results

def test_streamlit_initialization():
    """Test Streamlit app initialization"""
    print("🔍 Testing Streamlit App Initialization...")
    results = []
    
    try:
        from GetInternationalStandards import InternationalStandardsApp
        app = InternationalStandardsApp()
        results.append("✅ InternationalStandardsApp initializes successfully")
        
        # Test directory creation
        if app.config_dir.exists():
            results.append("✅ Config directory exists")
        else:
            results.append("❌ Config directory missing")
            
        if app.recovery_dir.exists():
            results.append("✅ Recovery directory exists")
        else:
            results.append("❌ Recovery directory missing")
            
        if app.data_dir.exists():
            results.append("✅ Data directory exists")  
        else:
            results.append("❌ Data directory missing")
            
    except Exception as e:
        results.append(f"❌ Streamlit app initialization failed: {str(e)[:100]}")
    
    return results

def test_llm_integration():
    """Test LLM integration functionality"""
    print("🔍 Testing LLM Integration...")
    results = []
    
    try:
        from core.llm_integration import LLMIntegration, TaskRequest
        
        # Test initialization
        config = {
            'llm_router_integration': {
                'auto_refresh_enabled': False,
                'refresh_interval_minutes': 60
            }
        }
        llm = LLMIntegration(config)
        results.append("✅ LLM Integration initializes")
        
        # Test task routing
        task = TaskRequest(
            prompt="Test educational standards analysis",
            task_type="classification", 
            discipline="Mathematics"
        )
        
        routing_result = llm.route_task(task)
        if 'recommended_model' in routing_result:
            results.append("✅ LLM task routing works")
        else:
            results.append("❌ LLM task routing failed")
            
    except Exception as e:
        results.append(f"❌ LLM Integration failed: {str(e)[:100]}")
    
    return results

def test_database_schema():
    """Test database schema functionality"""
    print("🔍 Testing Database Schema...")
    results = []
    
    try:
        from data.database_manager import DatabaseManager, DatabaseConfig
        
        # Test SQLite configuration
        config = DatabaseConfig(
            database_type="sqlite",
            sqlite_path=":memory:"  # In-memory for testing
        )
        
        db = DatabaseManager(config)
        results.append("✅ DatabaseManager initializes with SQLite")
        
        # Test basic database functionality
        connection = db.get_connection()
        if connection:
            results.append("✅ Database connection works")
            db.return_connection(connection)
        else:
            results.append("❌ Database connection failed")
        
    except Exception as e:
        results.append(f"❌ Database functionality failed: {str(e)[:100]}")
    
    return results

def test_quality_scoring():
    """Test quality scoring system"""
    print("🔍 Testing Quality Scoring System...")
    results = []
    
    try:
        from quality.quality_scoring import QualityScoringEngine, QualityDimension
        from data.database_manager import DatabaseManager, DatabaseConfig
        
        # Create database manager for scoring engine
        config = DatabaseConfig(database_type="sqlite", sqlite_path=":memory:")
        db = DatabaseManager(config)
        
        # Initialize scoring engine
        engine = QualityScoringEngine(db)
        results.append("✅ QualityScoringEngine initializes")
        
        # Test dimension enumeration
        dimensions = list(QualityDimension)
        if len(dimensions) >= 5:  # Should have multiple dimensions
            results.append(f"✅ Quality dimensions defined ({len(dimensions)} dimensions)")
        else:
            results.append("❌ Quality dimensions insufficient")
            
    except Exception as e:
        results.append(f"❌ Quality scoring failed: {str(e)[:100]}")
    
    return results

def test_api_generation():
    """Test API generation system"""
    print("🔍 Testing API Generation...")
    results = []
    
    try:
        from api.api_generator import APIGenerator
        from data.database_manager import DatabaseManager, DatabaseConfig
        
        # Create in-memory database for testing
        config = DatabaseConfig(database_type="sqlite", sqlite_path=":memory:")
        db = DatabaseManager(config)
        
        # Test API generator
        api_gen = APIGenerator(database_manager=db, framework="flask")
        results.append("✅ APIGenerator initializes with Flask")
        
        # Test OpenAPI spec generation
        spec = api_gen.generate_openapi_spec()
        if 'openapi' in spec and 'paths' in spec:
            results.append("✅ OpenAPI specification generation works")
        else:
            results.append("❌ OpenAPI specification incomplete")
            
    except Exception as e:
        results.append(f"❌ API generation failed: {str(e)[:100]}")
    
    return results

def main():
    """Run all debug tests"""
    print("🚀 INTERNATIONAL STANDARDS SYSTEM - DEBUG TESTING")
    print("=" * 80)
    print(f"Test execution started: {datetime.now()}")
    print()
    
    all_results = []
    test_functions = [
        test_core_imports,
        test_configuration_files,
        test_streamlit_initialization,
        test_llm_integration,
        test_database_schema,
        test_quality_scoring,
        test_api_generation
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_func in test_functions:
        try:
            results = test_func()
            all_results.extend(results)
            
            # Count results
            for result in results:
                total_tests += 1
                if result.startswith("✅"):
                    passed_tests += 1
                    
            # Print results
            for result in results:
                print(result)
            print()
            
        except Exception as e:
            error_msg = f"❌ {test_func.__name__} crashed: {str(e)}"
            print(error_msg)
            all_results.append(error_msg)
            total_tests += 1
            print()
    
    # Print summary
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print("=" * 80)
    print("🎯 TEST EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Total Tests Run: {total_tests}")
    print(f"✅ Tests Passed: {passed_tests}")
    print(f"❌ Tests Failed: {failed_tests}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    print(f"⏱️  Execution Time: {datetime.now()}")
    
    if success_rate >= 90:
        print("🎉 SYSTEM STATUS: EXCELLENT - Ready for Production")
    elif success_rate >= 80:
        print("✨ SYSTEM STATUS: GOOD - Minor issues detected")
    elif success_rate >= 70:
        print("⚠️  SYSTEM STATUS: ACCEPTABLE - Some issues need attention")
    else:
        print("🚨 SYSTEM STATUS: NEEDS WORK - Multiple issues detected")
    
    print("=" * 80)
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)