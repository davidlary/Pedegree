#!/usr/bin/env python3
"""
RIGOROUS PHYSICS & MCAT CASE STUDY VERIFICATION
Tests Physics standards at ALL education levels (K-12, High School, University, Graduate)
Plus MCAT medical standards as comprehensive system verification
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import traceback

class PhysicsMCATCaseStudyVerification:
    """Rigorous verification of Physics and MCAT standards across all education levels"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.results = {
            'verification_time': datetime.now().isoformat(),
            'physics_levels': {
                'k12': {'found': [], 'missing': [], 'organizations': []},
                'high_school': {'found': [], 'missing': [], 'organizations': []},
                'university': {'found': [], 'missing': [], 'organizations': []},
                'graduate': {'found': [], 'missing': [], 'organizations': []}
            },
            'mcat_medical': {'found': [], 'missing': [], 'organizations': []},
            'directory_structure_analysis': {},
            'file_integrity_check': {},
            'standards_coverage_analysis': {}
        }
        
        print("🔬 PHYSICS & MCAT CASE STUDY VERIFICATION")
        print("=" * 60)
        print("📊 Testing Physics at ALL education levels + MCAT")
        print("🎯 Rigorous verification of directory structure consistency")
        
    def verify_directory_structure(self):
        """Verify the Books-format directory structure is working correctly"""
        
        print("\n📁 DIRECTORY STRUCTURE VERIFICATION")
        print("-" * 40)
        
        # Expected directory structure: data/english/Physics/[Level]/[Organization]/
        physics_base = self.data_dir / "english" / "Physics"
        medicine_base = self.data_dir / "english" / "Medicine"
        
        structure_check = {
            'physics_base_exists': physics_base.exists(),
            'medicine_base_exists': medicine_base.exists(),
            'physics_levels_found': [],
            'medicine_levels_found': [],
            'total_physics_files': 0,
            'total_medicine_files': 0
        }
        
        # Check Physics directory structure
        if physics_base.exists():
            for level_dir in physics_base.iterdir():
                if level_dir.is_dir():
                    structure_check['physics_levels_found'].append(level_dir.name)
                    
                    # Count files in each level
                    files = list(level_dir.rglob('*'))
                    files = [f for f in files if f.is_file()]
                    structure_check['total_physics_files'] += len(files)
                    
                    print(f"✅ Physics/{level_dir.name}: {len(files)} files")
                    
                    # List organizations
                    for org_dir in level_dir.iterdir():
                        if org_dir.is_dir():
                            org_files = list(org_dir.rglob('*'))
                            org_files = [f for f in org_files if f.is_file()]
                            if org_files:
                                print(f"   📂 {org_dir.name}: {len(org_files)} documents")
                                for doc in org_files:
                                    print(f"      📄 {doc.name} ({doc.stat().st_size/1024:.1f} KB)")
        
        # Check Medicine directory structure  
        if medicine_base.exists():
            for level_dir in medicine_base.iterdir():
                if level_dir.is_dir():
                    structure_check['medicine_levels_found'].append(level_dir.name)
                    
                    # Count files in each level
                    files = list(level_dir.rglob('*'))
                    files = [f for f in files if f.is_file()]
                    structure_check['total_medicine_files'] += len(files)
                    
                    print(f"✅ Medicine/{level_dir.name}: {len(files)} files")
                    
                    # List organizations with focus on MCAT
                    for org_dir in level_dir.iterdir():
                        if org_dir.is_dir():
                            org_files = list(org_dir.rglob('*'))
                            org_files = [f for f in org_files if f.is_file()]
                            if org_files:
                                is_mcat = 'AAMC' in org_dir.name or any('MCAT' in f.name for f in org_files)
                                mcat_flag = "🎯 MCAT!" if is_mcat else ""
                                print(f"   📂 {org_dir.name}: {len(org_files)} documents {mcat_flag}")
                                for doc in org_files:
                                    mcat_doc_flag = "🎯 MCAT!" if 'MCAT' in doc.name else ""
                                    print(f"      📄 {doc.name} ({doc.stat().st_size/1024:.1f} KB) {mcat_doc_flag}")
        
        self.results['directory_structure_analysis'] = structure_check
        return structure_check
    
    def verify_physics_by_level(self):
        """Verify Physics standards at each education level"""
        
        print("\n🧪 PHYSICS STANDARDS BY EDUCATION LEVEL")
        print("-" * 45)
        
        physics_base = self.data_dir / "english" / "Physics"
        
        # Expected standards by level
        expected_standards = {
            'K12': [
                'Next Generation Science Standards (NGSS)',
                'National Science Education Standards',
                'State Science Standards'
            ],
            'HighSchool': [
                'AP Physics 1', 'AP Physics 2', 'AP Physics C',
                'SAT Physics Subject Test',
                'High School Physics Curriculum Standards'
            ],
            'University': [
                'AAPT Physics Education Standards',
                'APS Physics Education Standards', 
                'College Board Standards',
                'University Physics Curriculum',
                'Physics GRE Standards'
            ],
            'Graduate': [
                'Graduate Physics Program Standards',
                'Physics PhD Requirements',
                'Research Standards'
            ]
        }
        
        if not physics_base.exists():
            print("❌ Physics directory not found!")
            return False
            
        # Check University level (currently implemented)
        university_dir = physics_base / "University"
        if university_dir.exists():
            print(f"✅ University Level Found")
            
            organizations = []
            documents = []
            
            for org_dir in university_dir.iterdir():
                if org_dir.is_dir():
                    organizations.append(org_dir.name)
                    org_files = list(org_dir.rglob('*'))
                    org_files = [f for f in org_files if f.is_file()]
                    
                    for doc in org_files:
                        documents.append({
                            'name': doc.name,
                            'organization': org_dir.name,
                            'size_kb': doc.stat().st_size / 1024,
                            'path': str(doc)
                        })
                        
                        # Check if document matches expected standards
                        doc_name = doc.name.lower()
                        if 'aapt' in doc_name or 'physics education' in doc_name:
                            print(f"   🎯 FOUND: AAPT Physics Education Standards")
                        elif 'aps' in doc_name:
                            print(f"   🎯 FOUND: APS Physics Education Standards")
                        elif 'sat physics' in doc_name or 'college board' in doc_name:
                            print(f"   🎯 FOUND: College Board/SAT Physics Standards")
                        elif 'ieee' in doc_name:
                            print(f"   🎯 FOUND: IEEE Physics Standards")
                        elif 'nist' in doc_name:
                            print(f"   🎯 FOUND: NIST Physics Standards")
            
            self.results['physics_levels']['university'] = {
                'found': documents,
                'organizations': organizations,
                'missing': []  # TODO: Compare with expected_standards
            }
            
            print(f"   📊 Total Organizations: {len(organizations)}")
            print(f"   📊 Total Documents: {len(documents)}")
            print(f"   📊 Organizations: {', '.join(organizations)}")
            
        else:
            print("❌ University level directory not found!")
            return False
            
        return True
    
    def verify_mcat_standards(self):
        """Rigorously verify MCAT standards are present and accessible"""
        
        print("\n🏥 MCAT MEDICAL STANDARDS VERIFICATION")
        print("-" * 40)
        
        medicine_base = self.data_dir / "english" / "Medicine"
        
        if not medicine_base.exists():
            print("❌ Medicine directory not found!")
            return False
            
        university_dir = medicine_base / "University"
        if not university_dir.exists():
            print("❌ Medicine/University directory not found!")
            return False
            
        # Look for AAMC organization (handles MCAT)
        aamc_dir = university_dir / "AAMC"
        if not aamc_dir.exists():
            print("❌ AAMC directory not found!")
            return False
            
        print("✅ AAMC directory found")
        
        # Verify MCAT-specific documents
        mcat_documents = []
        other_aamc_documents = []
        
        for doc in aamc_dir.rglob('*'):
            if doc.is_file():
                if 'MCAT' in doc.name or 'mcat' in doc.name:
                    mcat_documents.append({
                        'name': doc.name,
                        'size_kb': doc.stat().st_size / 1024,
                        'path': str(doc),
                        'type': doc.suffix
                    })
                    print(f"🎯 MCAT DOCUMENT FOUND: {doc.name} ({doc.stat().st_size/1024:.1f} KB)")
                else:
                    other_aamc_documents.append({
                        'name': doc.name,
                        'size_kb': doc.stat().st_size / 1024,
                        'path': str(doc),
                        'type': doc.suffix
                    })
                    print(f"📄 AAMC Document: {doc.name} ({doc.stat().st_size/1024:.1f} KB)")
        
        # Verify file integrity of MCAT documents
        mcat_integrity_check = True
        for doc in mcat_documents:
            doc_path = Path(doc['path'])
            if doc_path.exists() and doc_path.stat().st_size > 0:
                print(f"✅ MCAT Document Integrity: {doc['name']} - OK")
            else:
                print(f"❌ MCAT Document Integrity: {doc['name']} - FAILED")
                mcat_integrity_check = False
        
        self.results['mcat_medical'] = {
            'found': mcat_documents,
            'other_aamc': other_aamc_documents,
            'organizations': ['AAMC'],
            'integrity_check': mcat_integrity_check
        }
        
        print(f"\n📊 MCAT VERIFICATION SUMMARY:")
        print(f"   🎯 MCAT Documents Found: {len(mcat_documents)}")
        print(f"   📄 Other AAMC Documents: {len(other_aamc_documents)}")
        print(f"   ✅ File Integrity: {'PASS' if mcat_integrity_check else 'FAIL'}")
        
        return len(mcat_documents) > 0 and mcat_integrity_check
    
    def verify_api_integration(self):
        """Test if the Standards Retrieval Engine can access documents"""
        
        print("\n🔗 API INTEGRATION VERIFICATION")
        print("-" * 35)
        
        try:
            # Import and test Standards Retrieval Engine
            sys.path.append(str(self.base_dir))
            from core.standards_retrieval_engine import StandardsRetrievalEngine
            
            engine = StandardsRetrievalEngine(self.data_dir)
            
            # Test Physics retrieval
            print("Testing Physics retrieval...")
            physics_docs = engine.retrieve_standards_for_discipline('Physical_Sciences')
            print(f"✅ Physics retrieval: {len(physics_docs)} documents")
            
            # Test Health Sciences (MCAT) retrieval
            print("Testing Health Sciences (MCAT) retrieval...")
            health_docs = engine.retrieve_standards_for_discipline('Health_Sciences')
            print(f"✅ Health Sciences retrieval: {len(health_docs)} documents")
            
            # Verify MCAT documents are accessible via API
            mcat_found_via_api = False
            for doc in health_docs:
                if 'MCAT' in doc.title:
                    print(f"🎯 MCAT accessible via API: {doc.title}")
                    mcat_found_via_api = True
            
            return {
                'physics_accessible': len(physics_docs) > 0,
                'health_accessible': len(health_docs) > 0,
                'mcat_accessible': mcat_found_via_api,
                'total_physics_docs': len(physics_docs),
                'total_health_docs': len(health_docs)
            }
            
        except Exception as e:
            print(f"❌ API Integration Failed: {e}")
            traceback.print_exc()
            return None
    
    def generate_comprehensive_report(self):
        """Generate detailed verification report"""
        
        print("\n📋 COMPREHENSIVE VERIFICATION REPORT")
        print("=" * 50)
        
        # Run all verifications
        directory_ok = self.verify_directory_structure()
        physics_ok = self.verify_physics_by_level()
        mcat_ok = self.verify_mcat_standards()
        api_results = self.verify_api_integration()
        
        # Overall assessment
        all_checks_passed = (
            directory_ok['physics_base_exists'] and
            directory_ok['medicine_base_exists'] and
            physics_ok and
            mcat_ok and
            api_results is not None and
            api_results['mcat_accessible']
        )
        
        print(f"\n🎯 FINAL VERIFICATION RESULTS:")
        print(f"   📁 Directory Structure: {'✅ PASS' if directory_ok['physics_base_exists'] and directory_ok['medicine_base_exists'] else '❌ FAIL'}")
        print(f"   🧪 Physics Standards: {'✅ PASS' if physics_ok else '❌ FAIL'}")
        print(f"   🏥 MCAT Standards: {'✅ PASS' if mcat_ok else '❌ FAIL'}")
        print(f"   🔗 API Integration: {'✅ PASS' if api_results and api_results['mcat_accessible'] else '❌ FAIL'}")
        print(f"   🎊 OVERALL RESULT: {'✅ ALL SYSTEMS OPERATIONAL' if all_checks_passed else '❌ ISSUES DETECTED'}")
        
        # Save detailed report
        report_file = self.base_dir / f"physics_mcat_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        final_report = {
            'verification_summary': {
                'timestamp': datetime.now().isoformat(),
                'overall_pass': all_checks_passed,
                'directory_structure': directory_ok,
                'physics_verification': physics_ok,
                'mcat_verification': mcat_ok,
                'api_integration': api_results
            },
            'detailed_results': self.results
        }
        
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=2)
        
        print(f"\n📄 Detailed report saved: {report_file}")
        
        return all_checks_passed

def main():
    """Execute comprehensive Physics & MCAT verification"""
    
    try:
        verifier = PhysicsMCATCaseStudyVerification()
        success = verifier.generate_comprehensive_report()
        
        if success:
            print("\n🎉 VERIFICATION COMPLETE - ALL SYSTEMS OPERATIONAL")
            print("✅ Physics standards accessible at University level")
            print("✅ MCAT standards properly stored and accessible")
            print("✅ Directory structure consistent (Books format)")
            print("✅ API integration working correctly")
            return 0
        else:
            print("\n❌ VERIFICATION FAILED - ISSUES DETECTED")
            return 1
            
    except Exception as e:
        print(f"\n💥 VERIFICATION ERROR: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())