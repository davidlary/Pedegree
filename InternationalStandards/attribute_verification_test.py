#!/usr/bin/env python3
"""
CRITICAL ATTRIBUTE VERIFICATION TEST
Specifically test for missing attributes like database_manager
"""

def test_critical_attributes():
    """Test all critical attributes exist"""
    print("🔍 CRITICAL ATTRIBUTE VERIFICATION TEST")
    print("=" * 50)
    
    critical_errors = []
    
    try:
        print("Importing InternationalStandardsApp...")
        from GetInternationalStandards import InternationalStandardsApp
        
        print("Creating app instance...")
        app = InternationalStandardsApp()
        print("✅ App instance created successfully")
        
        # Check critical attributes
        critical_attributes = [
            'config',
            'orchestrator', 
            'recovery_manager',
            'cache',
            'database_manager',  # This was missing!
            'data_dir',
            'config_dir',
            'recovery_dir'
        ]
        
        print(f"\nChecking {len(critical_attributes)} critical attributes...")
        
        missing_attributes = []
        none_attributes = []
        
        for attr in critical_attributes:
            print(f"  Checking {attr}...", end=" ")
            
            if not hasattr(app, attr):
                missing_attributes.append(attr)
                print("❌ MISSING")
                critical_errors.append(f"Missing attribute: {attr}")
            elif getattr(app, attr) is None:
                none_attributes.append(attr)
                print("⚠️  None")
                critical_errors.append(f"None attribute: {attr}")
            else:
                print("✅ OK")
        
        # Test Standards Browser specifically
        print(f"\n📚 TESTING STANDARDS BROWSER PAGE ACCESS...")
        try:
            # This is where the database_manager error occurred
            if hasattr(app, '_render_standards_browser'):
                print("  _render_standards_browser method exists...")
                
                # Try to call it (this will likely fail if database_manager is missing)
                app._render_standards_browser()
                print("  ✅ Standards Browser method executed without AttributeError")
                
            else:
                print("  ❌ _render_standards_browser method missing")
                critical_errors.append("Missing _render_standards_browser method")
                
        except AttributeError as e:
            if 'database_manager' in str(e):
                print(f"  ❌ CRITICAL: database_manager AttributeError: {e}")
                critical_errors.append(f"Standards Browser database_manager error: {e}")
            else:
                print(f"  ⚠️  Other AttributeError: {e}")
                
        except Exception as e:
            print(f"  ⚠️  Other error (may be expected): {e}")
        
        # Test all page methods
        print(f"\n📄 TESTING ALL PAGE METHODS...")
        page_methods = [
            '_render_dashboard',
            '_render_standards_browser',
            '_render_agent_monitor',
            '_render_discipline_explorer',
            '_render_llm_optimization',
            '_render_data_apis',
            '_render_recovery_center'
        ]
        
        missing_methods = []
        for method in page_methods:
            if hasattr(app, method):
                print(f"  ✅ {method}")
            else:
                print(f"  ❌ {method} MISSING")
                missing_methods.append(method)
        
        if missing_methods:
            critical_errors.extend([f"Missing method: {m}" for m in missing_methods])
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"  Missing attributes: {len(missing_attributes)}")
        print(f"  None attributes: {len(none_attributes)}")
        print(f"  Missing methods: {len(missing_methods)}")
        print(f"  Total critical errors: {len(critical_errors)}")
        
        if missing_attributes:
            print(f"\n❌ MISSING ATTRIBUTES:")
            for attr in missing_attributes:
                print(f"    • {attr}")
        
        if none_attributes:
            print(f"\n⚠️  NONE ATTRIBUTES:")
            for attr in none_attributes:
                print(f"    • {attr}")
        
        if critical_errors:
            print(f"\n❌ ALL CRITICAL ERRORS:")
            for error in critical_errors:
                print(f"    • {error}")
            
            print(f"\n❌ RESULT: NOT PRODUCTION READY")
            print(f"   {len(critical_errors)} critical issues must be fixed")
            return False
        else:
            print(f"\n✅ RESULT: ALL CRITICAL ATTRIBUTES PRESENT")
            print("   No critical attribute errors found")
            return True
            
    except Exception as e:
        print(f"\n❌ CRITICAL FAILURE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_critical_attributes()
    exit(0 if success else 1)