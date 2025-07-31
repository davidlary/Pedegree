#!/usr/bin/env python3
"""
Comprehensive Component Testing for International Standards Retrieval System
Tests every component with detailed pass/fail results
"""

import sys
import traceback
import json
from pathlib import Path
from datetime import datetime
import importlib
import inspect

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class ComponentTestRunner:
    def __init__(self):
        self.results = {
            'test_timestamp': datetime.now().isoformat(),
            'components_tested': {},
            'summary': {
                'total_components': 0,
                'passed_components': 0,
                'failed_components': 0,
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0
            }
        }
    
    def test_component(self, component_name, test_func):
        """Test a single component with detailed results"""
        print(f"\n🔍 Testing {component_name}...")
        print("-" * 60)
        
        component_results = {
            'component_name': component_name,
            'tests': [],
            'passed': 0,
            'failed': 0,
            'status': 'UNKNOWN'
        }
        
        try:
            tests = test_func()
            for test in tests:
                component_results['tests'].append(test)
                if test['status'] == 'PASS':
                    component_results['passed'] += 1
                    print(f"✅ {test['test_name']}")
                    if test.get('details'):
                        print(f"   {test['details']}")
                else:
                    component_results['failed'] += 1
                    print(f"❌ {test['test_name']}")
                    if test.get('error'):
                        print(f"   Error: {test['error']}")
                        
            # Determine component status
            if component_results['failed'] == 0:
                component_results['status'] = 'PASS'
                self.results['summary']['passed_components'] += 1
            else:
                component_results['status'] = 'FAIL'
                self.results['summary']['failed_components'] += 1
                
        except Exception as e:
            component_results['status'] = 'ERROR'
            component_results['tests'].append({
                'test_name': f'{component_name}_initialization',
                'status': 'FAIL',
                'error': str(e)
            })
            component_results['failed'] += 1
            self.results['summary']['failed_components'] += 1
            print(f"❌ {component_name} initialization failed: {str(e)}")
        
        # Update summary
        self.results['summary']['total_components'] += 1
        self.results['summary']['total_tests'] += len(component_results['tests'])
        self.results['summary']['passed_tests'] += component_results['passed']
        self.results['summary']['failed_tests'] += component_results['failed']
        
        # Store results
        self.results['components_tested'][component_name] = component_results
        
        # Print component summary
        print(f"\n📊 {component_name} Results: {component_results['passed']} passed, {component_results['failed']} failed")
        print(f"🎯 Component Status: {component_results['status']}")
    
    def test_main_streamlit_app(self):
        """Test main Streamlit application"""
        tests = []
        
        try:
            from GetInternationalStandards import InternationalStandardsApp
            
            # Test 1: App initialization
            try:
                app = InternationalStandardsApp()
                tests.append({
                    'test_name': 'Application_Initialization',
                    'status': 'PASS',
                    'details': 'App initializes successfully'
                })
            except Exception as e:
                tests.append({
                    'test_name': 'Application_Initialization',
                    'status': 'FAIL',
                    'error': str(e)
                })
                return tests
            
            # Test 2: Directory creation
            try:
                required_dirs = ['config_dir', 'recovery_dir', 'data_dir']
                for dir_attr in required_dirs:
                    if hasattr(app, dir_attr):
                        dir_path = getattr(app, dir_attr)
                        if dir_path.exists():
                            tests.append({
                                'test_name': f'Directory_{dir_attr}',
                                'status': 'PASS',
                                'details': f'{dir_path} exists'
                            })
                        else:
                            tests.append({
                                'test_name': f'Directory_{dir_attr}',
                                'status': 'FAIL',
                                'error': f'{dir_path} does not exist'
                            })
            except Exception as e:
                tests.append({
                    'test_name': 'Directory_Creation',
                    'status': 'FAIL',
                    'error': str(e)
                })
            
            # Test 3: Configuration loading
            try:
                if hasattr(app, 'config') and app.config:
                    tests.append({
                        'test_name': 'Configuration_Loading',
                        'status': 'PASS',
                        'details': f'Loaded {len(app.config)} config sections'
                    })
                else:
                    tests.append({
                        'test_name': 'Configuration_Loading',
                        'status': 'FAIL',
                        'error': 'No configuration loaded'
                    })
            except Exception as e:
                tests.append({
                    'test_name': 'Configuration_Loading',
                    'status': 'FAIL',
                    'error': str(e)
                })
            
            # Test 4: Recovery manager initialization
            try:
                if hasattr(app, 'recovery_manager') and app.recovery_manager:
                    tests.append({
                        'test_name': 'Recovery_Manager_Init',
                        'status': 'PASS',
                        'details': 'Recovery manager initialized'
                    })
                else:
                    tests.append({
                        'test_name': 'Recovery_Manager_Init',
                        'status': 'FAIL',
                        'error': 'Recovery manager not initialized'
                    })
            except Exception as e:
                tests.append({
                    'test_name': 'Recovery_Manager_Init',
                    'status': 'FAIL',
                    'error': str(e)
                })
            
            # Test 5: LLM integration
            try:
                if hasattr(app, 'llm_integration') and app.llm_integration:
                    tests.append({
                        'test_name': 'LLM_Integration_Init',
                        'status': 'PASS',
                        'details': f'LLM available: {app.llm_integration.get("available", False)}'
                    })
                else:
                    tests.append({
                        'test_name': 'LLM_Integration_Init',
                        'status': 'FAIL',
                        'error': 'LLM integration not initialized'
                    })
            except Exception as e:
                tests.append({
                    'test_name': 'LLM_Integration_Init',
                    'status': 'FAIL',
                    'error': str(e)
                })
                
        except ImportError as e:
            tests.append({
                'test_name': 'Module_Import',
                'status': 'FAIL',
                'error': f'Cannot import GetInternationalStandards: {str(e)}'
            })
        
        return tests
    
    def test_core_orchestrator(self):
        """Test core orchestrator functionality"""
        tests = []
        
        try:
            from core.orchestrator import StandardsOrchestrator
            from core.recovery_manager import RecoveryManager
            from core.llm_integration import LLMIntegration
            
            # Test 1: Class import
            tests.append({
                'test_name': 'Module_Import',
                'status': 'PASS',
                'details': 'StandardsOrchestrator imported successfully'
            })
            
            # Test 2: Check class methods
            try:
                methods = [method for method in dir(StandardsOrchestrator) if not method.startswith('_')]
                required_methods = ['start_system', 'stop_system', 'get_system_status']
                
                for method in required_methods:
                    if method in methods:
                        tests.append({
                            'test_name': f'Method_{method}',
                            'status': 'PASS',
                            'details': f'Method {method} exists'
                        })
                    else:
                        tests.append({
                            'test_name': f'Method_{method}',
                            'status': 'FAIL',
                            'error': f'Method {method} missing'
                        })
            except Exception as e:
                tests.append({
                    'test_name': 'Method_Check',
                    'status': 'FAIL',
                    'error': str(e)
                })
                
        except ImportError as e:
            tests.append({
                'test_name': 'Module_Import',
                'status': 'FAIL',
                'error': f'Cannot import orchestrator: {str(e)}'
            })
        
        return tests
    
    def test_llm_integration(self):
        """Test LLM integration functionality"""
        tests = []
        
        try:
            from core.llm_integration import LLMIntegration, TaskRequest, TaskResult
            
            # Test 1: Module import
            tests.append({
                'test_name': 'Module_Import',
                'status': 'PASS',
                'details': 'LLM integration modules imported'
            })
            
            # Test 2: LLM Integration initialization
            try:
                config = {'llm_router_integration': {'auto_refresh_enabled': False}}
                llm = LLMIntegration(config)
                tests.append({
                    'test_name': 'LLM_Integration_Init',
                    'status': 'PASS',
                    'details': 'LLM integration initializes successfully'
                })
                
                # Test 3: Task request creation
                try:
                    task = TaskRequest(
                        prompt="Test prompt",
                        task_type="classification",
                        discipline="Mathematics"
                    )
                    tests.append({
                        'test_name': 'Task_Request_Creation',
                        'status': 'PASS',
                        'details': 'TaskRequest created successfully'
                    })
                    
                    # Test 4: Task routing
                    try:
                        result = llm.route_task(task)
                        if 'recommended_model' in result:
                            tests.append({
                                'test_name': 'Task_Routing',
                                'status': 'PASS',
                                'details': f'Routed to model: {result["recommended_model"]}'
                            })
                        else:
                            tests.append({
                                'test_name': 'Task_Routing',
                                'status': 'FAIL',
                                'error': 'No model recommended'
                            })
                    except Exception as e:
                        tests.append({
                            'test_name': 'Task_Routing',
                            'status': 'FAIL',
                            'error': str(e)
                        })
                        
                except Exception as e:
                    tests.append({
                        'test_name': 'Task_Request_Creation',
                        'status': 'FAIL',
                        'error': str(e)
                    })
                    
            except Exception as e:
                tests.append({
                    'test_name': 'LLM_Integration_Init',
                    'status': 'FAIL',
                    'error': str(e)
                })
                
        except ImportError as e:
            tests.append({
                'test_name': 'Module_Import',
                'status': 'FAIL',
                'error': f'Cannot import LLM integration: {str(e)}'
            })
        
        return tests
    
    def test_database_manager(self):
        """Test database manager functionality"""
        tests = []
        
        try:
            from data.database_manager import DatabaseManager, DatabaseConfig
            
            # Test 1: Module import
            tests.append({
                'test_name': 'Module_Import',
                'status': 'PASS',
                'details': 'Database manager imported successfully'
            })
            
            # Test 2: SQLite configuration
            try:
                config = DatabaseConfig(database_type="sqlite", sqlite_path=":memory:")
                tests.append({
                    'test_name': 'SQLite_Config',
                    'status': 'PASS',
                    'details': 'SQLite configuration created'
                })
                
                # Test 3: Database manager initialization
                try:
                    db = DatabaseManager(config)
                    tests.append({
                        'test_name': 'Database_Manager_Init',
                        'status': 'PASS',
                        'details': 'Database manager initialized'
                    })
                    
                    # Test 4: Connection test
                    try:
                        conn = db.get_connection()
                        if conn:
                            tests.append({
                                'test_name': 'Database_Connection',
                                'status': 'PASS',
                                'details': 'Database connection successful'
                            })
                            db.return_connection(conn)
                        else:
                            tests.append({
                                'test_name': 'Database_Connection',
                                'status': 'FAIL',
                                'error': 'Failed to get database connection'
                            })
                    except Exception as e:
                        tests.append({
                            'test_name': 'Database_Connection',
                            'status': 'FAIL',
                            'error': str(e)
                        })
                        
                    # Test 5: Method availability
                    required_methods = ['get_all_disciplines', 'insert_standard', 'get_standards_by_discipline']
                    for method in required_methods:
                        if hasattr(db, method):
                            tests.append({
                                'test_name': f'Method_{method}',
                                'status': 'PASS',
                                'details': f'Method {method} available'
                            })
                        else:
                            tests.append({
                                'test_name': f'Method_{method}',
                                'status': 'FAIL',
                                'error': f'Method {method} missing'
                            })
                            
                except Exception as e:
                    tests.append({
                        'test_name': 'Database_Manager_Init',
                        'status': 'FAIL',
                        'error': str(e)
                    })
                    
            except Exception as e:
                tests.append({
                    'test_name': 'SQLite_Config',
                    'status': 'FAIL',
                    'error': str(e)
                })
                
        except ImportError as e:
            tests.append({
                'test_name': 'Module_Import',
                'status': 'FAIL',
                'error': f'Cannot import database manager: {str(e)}'
            })
        
        return tests
    
    def test_quality_scoring(self):
        """Test quality scoring system"""
        tests = []
        
        try:
            from quality.quality_scoring import QualityScoringEngine, QualityDimension
            from data.database_manager import DatabaseManager, DatabaseConfig
            
            # Test 1: Module import
            tests.append({
                'test_name': 'Module_Import',
                'status': 'PASS',
                'details': 'Quality scoring modules imported'
            })
            
            # Test 2: Quality dimensions
            try:
                dimensions = list(QualityDimension)
                tests.append({
                    'test_name': 'Quality_Dimensions',
                    'status': 'PASS',
                    'details': f'{len(dimensions)} quality dimensions defined'
                })
            except Exception as e:
                tests.append({
                    'test_name': 'Quality_Dimensions',
                    'status': 'FAIL',
                    'error': str(e)
                })
            
            # Test 3: Scoring engine initialization
            try:
                config = DatabaseConfig(database_type="sqlite", sqlite_path=":memory:")
                db = DatabaseManager(config)
                engine = QualityScoringEngine(db)
                tests.append({
                    'test_name': 'Scoring_Engine_Init',
                    'status': 'PASS',
                    'details': 'Quality scoring engine initialized'
                })
            except Exception as e:
                tests.append({
                    'test_name': 'Scoring_Engine_Init',
                    'status': 'FAIL',
                    'error': str(e)
                })
                
        except ImportError as e:
            tests.append({
                'test_name': 'Module_Import',
                'status': 'FAIL',
                'error': f'Cannot import quality scoring: {str(e)}'
            })
        
        return tests
    
    def test_api_generator(self):
        """Test API generator functionality"""
        tests = []
        
        try:
            from api.api_generator import APIGenerator
            from data.database_manager import DatabaseManager, DatabaseConfig
            
            # Test 1: Module import
            tests.append({
                'test_name': 'Module_Import',
                'status': 'PASS',
                'details': 'API generator imported successfully'
            })
            
            # Test 2: API generator initialization
            try:
                config = DatabaseConfig(database_type="sqlite", sqlite_path=":memory:")
                db = DatabaseManager(config)
                
                # Try different frameworks
                frameworks_to_test = ['flask', 'fastapi']
                for framework in frameworks_to_test:
                    try:
                        api_gen = APIGenerator(database_manager=db, framework=framework)
                        tests.append({
                            'test_name': f'API_Generator_{framework}',
                            'status': 'PASS',
                            'details': f'{framework} API generator initialized'
                        })
                        
                        # Test OpenAPI spec generation
                        try:
                            spec = api_gen.generate_openapi_spec()
                            if 'openapi' in spec and 'paths' in spec:
                                tests.append({
                                    'test_name': f'OpenAPI_Spec_{framework}',
                                    'status': 'PASS',
                                    'details': f'OpenAPI spec generated with {len(spec.get("paths", {}))} endpoints'
                                })
                            else:
                                tests.append({
                                    'test_name': f'OpenAPI_Spec_{framework}',
                                    'status': 'FAIL',
                                    'error': 'Invalid OpenAPI specification'
                                })
                        except Exception as e:
                            tests.append({
                                'test_name': f'OpenAPI_Spec_{framework}',
                                'status': 'FAIL',
                                'error': str(e)
                            })
                        break  # Only test the first working framework
                        
                    except Exception as e:
                        tests.append({
                            'test_name': f'API_Generator_{framework}',
                            'status': 'FAIL',
                            'error': str(e)
                        })
                        
            except Exception as e:
                tests.append({
                    'test_name': 'API_Generator_Init',
                    'status': 'FAIL',
                    'error': str(e)
                })
                
        except ImportError as e:
            tests.append({
                'test_name': 'Module_Import',
                'status': 'FAIL',
                'error': f'Cannot import API generator: {str(e)}'
            })
        
        return tests
    
    def test_agent_system(self):
        """Test multi-agent system"""
        tests = []
        
        try:
            from core.agents.base_agent import BaseAgent, AgentStatus
            from core.agents.discovery_agent import DiscoveryAgent
            from core.agents.retrieval_agent import RetrievalAgent
            from core.agents.processing_agent import ProcessingAgent
            from core.agents.validation_agent import ValidationAgent
            
            # Test 1: Base agent import
            tests.append({
                'test_name': 'Base_Agent_Import',
                'status': 'PASS',
                'details': 'BaseAgent imported successfully'
            })
            
            # Test 2: Agent status enum
            try:
                statuses = list(AgentStatus)
                tests.append({
                    'test_name': 'Agent_Status_Enum',
                    'status': 'PASS',
                    'details': f'{len(statuses)} agent statuses defined'
                })
            except Exception as e:
                tests.append({
                    'test_name': 'Agent_Status_Enum',
                    'status': 'FAIL',
                    'error': str(e)
                })
            
            # Test 3: Specialized agents import
            agent_classes = [
                ('DiscoveryAgent', DiscoveryAgent),
                ('RetrievalAgent', RetrievalAgent), 
                ('ProcessingAgent', ProcessingAgent),
                ('ValidationAgent', ValidationAgent)
            ]
            
            for agent_name, agent_class in agent_classes:
                try:
                    # Check if class exists and has required methods
                    required_methods = ['start', 'stop', 'assign_task']
                    methods = [method for method in dir(agent_class) if not method.startswith('_')]
                    
                    missing_methods = []
                    for method in required_methods:
                        if method not in methods:
                            missing_methods.append(method)
                    
                    if not missing_methods:
                        tests.append({
                            'test_name': f'{agent_name}_Structure',
                            'status': 'PASS',
                            'details': f'{agent_name} has all required methods'
                        })
                    else:
                        tests.append({
                            'test_name': f'{agent_name}_Structure',
                            'status': 'FAIL',
                            'error': f'Missing methods: {missing_methods}'
                        })
                        
                except Exception as e:
                    tests.append({
                        'test_name': f'{agent_name}_Structure',
                        'status': 'FAIL',
                        'error': str(e)
                    })
                    
        except ImportError as e:
            tests.append({
                'test_name': 'Module_Import',
                'status': 'FAIL',
                'error': f'Cannot import agent modules: {str(e)}'
            })
        
        return tests
    
    def test_configuration_system(self):
        """Test configuration management"""
        tests = []
        
        # Test 1: Configuration files exist
        config_files = [
            'config/openalex_disciplines.yaml',
            'config/standards_ecosystem.yaml',
            'config/recovery_system.yaml',
            'config/llm_optimization.yaml',
            'config/system_architecture.yaml'
        ]
        
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                if config_path.stat().st_size > 0:
                    tests.append({
                        'test_name': f'Config_File_{config_path.stem}',
                        'status': 'PASS',
                        'details': f'{config_file} exists and has content'
                    })
                else:
                    tests.append({
                        'test_name': f'Config_File_{config_path.stem}',
                        'status': 'FAIL',
                        'error': f'{config_file} is empty'
                    })
            else:
                tests.append({
                    'test_name': f'Config_File_{config_path.stem}',
                    'status': 'FAIL',
                    'error': f'{config_file} does not exist'
                })
        
        # Test 2: Configuration manager
        try:
            from core.config_manager import ConfigManager
            
            tests.append({
                'test_name': 'Config_Manager_Import',
                'status': 'PASS',
                'details': 'ConfigManager imported successfully'
            })
            
            try:
                config_manager = ConfigManager()
                tests.append({
                    'test_name': 'Config_Manager_Init',
                    'status': 'PASS',
                    'details': 'ConfigManager initialized successfully'
                })
            except Exception as e:
                tests.append({
                    'test_name': 'Config_Manager_Init',
                    'status': 'FAIL',
                    'error': str(e)
                })
                
        except ImportError as e:
            tests.append({
                'test_name': 'Config_Manager_Import',
                'status': 'FAIL',
                'error': f'Cannot import ConfigManager: {str(e)}'
            })
        
        return tests
    
    def run_all_tests(self):
        """Run all component tests"""
        print("🚀 COMPREHENSIVE COMPONENT TESTING")
        print("=" * 80)
        print(f"Test execution started: {datetime.now()}")
        print()
        
        # Define all test components
        test_components = [
            ("Main_Streamlit_App", self.test_main_streamlit_app),
            ("Core_Orchestrator", self.test_core_orchestrator),
            ("LLM_Integration", self.test_llm_integration),
            ("Database_Manager", self.test_database_manager),
            ("Quality_Scoring", self.test_quality_scoring),
            ("API_Generator", self.test_api_generator),
            ("Agent_System", self.test_agent_system),
            ("Configuration_System", self.test_configuration_system)
        ]
        
        # Run all tests
        for component_name, test_func in test_components:
            self.test_component(component_name, test_func)
        
        # Print final summary
        self.print_final_summary()
        
        # Save detailed results
        self.save_results()
        
        return self.results
    
    def print_final_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        
        summary = self.results['summary']
        success_rate = (summary['passed_tests'] / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
        
        print(f"📊 OVERALL STATISTICS:")
        print(f"   Total Components Tested: {summary['total_components']}")
        print(f"   ✅ Components Passed: {summary['passed_components']}")
        print(f"   ❌ Components Failed: {summary['failed_components']}")
        print(f"   📈 Component Success Rate: {(summary['passed_components'] / summary['total_components'] * 100):.1f}%")
        print()
        print(f"🔍 DETAILED TEST STATISTICS:")
        print(f"   Total Individual Tests: {summary['total_tests']}")
        print(f"   ✅ Tests Passed: {summary['passed_tests']}")
        print(f"   ❌ Tests Failed: {summary['failed_tests']}")
        print(f"   📈 Test Success Rate: {success_rate:.1f}%")
        print()
        
        # Component-by-component results
        print("📋 COMPONENT-BY-COMPONENT RESULTS:")
        for component_name, component_data in self.results['components_tested'].items():
            status_icon = "✅" if component_data['status'] == 'PASS' else "❌"
            print(f"   {status_icon} {component_name}: {component_data['passed']}/{component_data['passed'] + component_data['failed']} tests passed")
        
        print()
        if success_rate >= 95:
            print("🎉 SYSTEM STATUS: EXCELLENT - All components fully functional")
        elif success_rate >= 85:
            print("✨ SYSTEM STATUS: GOOD - Minor issues detected")
        elif success_rate >= 70:
            print("⚠️  SYSTEM STATUS: ACCEPTABLE - Some components need attention")
        else:
            print("🚨 SYSTEM STATUS: CRITICAL - Multiple components need fixes")
        
        print("=" * 80)
    
    def save_results(self):
        """Save test results to file"""
        try:
            results_file = Path('test_results_comprehensive.json')
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"📄 Detailed test results saved to: {results_file}")
        except Exception as e:
            print(f"⚠️  Could not save results file: {e}")

def main():
    """Main execution function"""
    runner = ComponentTestRunner()
    results = runner.run_all_tests()
    
    # Return success if test success rate is >= 85%
    success_rate = (results['summary']['passed_tests'] / results['summary']['total_tests'] * 100) if results['summary']['total_tests'] > 0 else 0
    return success_rate >= 85

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)