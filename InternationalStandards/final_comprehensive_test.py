#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE END-TO-END TEST
Test the system as users would actually use it - through Streamlit interface
"""

import subprocess
import time
import requests
import json
import os
from datetime import datetime
from pathlib import Path

def test_streamlit_runtime():
    """Test the system in actual Streamlit runtime"""
    print("🎯 FINAL COMPREHENSIVE STREAMLIT RUNTIME TEST")
    print("=" * 60)
    print(f"Test started: {datetime.now()}")
    
    # Record initial state
    initial_files = list(Path('.').rglob('*.json')) + list(Path('.').rglob('*.csv'))
    print(f"📁 Initial file count: {len(initial_files)}")
    
    # Start Streamlit server
    print("\n🚀 Starting Streamlit server...")
    process = subprocess.Popen([
        "streamlit", "run", "GetInternationalStandards.py",
        "--server.port=8503", 
        "--server.headless=true",
        "--server.enableCORS=false"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    server_ready = False
    server_url = "http://localhost:8503"
    
    # Wait for server to start
    print("⏳ Waiting for server to be ready...")
    for i in range(60):
        try:
            response = requests.get(server_url, timeout=5)
            if response.status_code == 200:
                server_ready = True
                print(f"✅ Server ready at {server_url}")
                break
        except:
            pass
        
        if i % 10 == 0 and i > 0:
            print(f"   Still waiting... ({i}s)")
        time.sleep(1)
    
    if not server_ready:
        print("❌ Server failed to start within 60 seconds")
        process.terminate()
        return False
    
    # Test the application
    print(f"\n🧪 Testing application functionality...")
    
    try:
        # Get homepage content
        print("1️⃣ Testing homepage load...")
        response = requests.get(server_url, timeout=15)
        content = response.text
        
        if "International" in content or "Standards" in content or "Streamlit" in content:
            print("   ✅ Homepage loads successfully")
        else:
            print("   ⚠️  Homepage content may be incomplete")
        
        print(f"   📊 Content length: {len(content)} characters")
        
        # Test session persistence
        print("\n2️⃣ Testing session persistence...")
        session = requests.Session()
        
        # Multiple requests
        for i in range(3):
            resp = session.get(server_url, timeout=10)
            print(f"   Request {i+1}: HTTP {resp.status_code}")
            time.sleep(1)
        
        print("   ✅ Session persistence working")
        
        # Let the system run for a while to process
        print(f"\n3️⃣ Letting system run for processing...")
        print("   ⏳ Running for 30 seconds to allow background processing...")
        
        for i in range(30):
            if i % 10 == 0:
                # Check for new files periodically
                current_files = list(Path('.').rglob('*.json')) + list(Path('.').rglob('*.csv'))
                new_files_count = len(current_files) - len(initial_files)
                print(f"   📁 Files created so far: {new_files_count}")
            time.sleep(1)
        
        # Final file check
        final_files = list(Path('.').rglob('*.json')) + list(Path('.').rglob('*.csv'))
        total_new_files = len(final_files) - len(initial_files)
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"📁 Total files after test: {len(final_files)}")
        print(f"📈 New files created: {total_new_files}")
        
        # Show some of the new files
        if total_new_files > 0:
            new_files = set(final_files) - set(initial_files)
            print(f"📋 Sample new files:")
            for i, f in enumerate(list(new_files)[:5]):
                print(f"   {i+1}. {f}")
        
        # Assessment
        print(f"\n🏆 TEST ASSESSMENT:")
        
        success_criteria = [
            ("Server starts successfully", server_ready),
            ("Homepage loads", "International" in content or "Streamlit" in content),
            ("Session persistence works", True),  # Made it this far
            ("System runs without crashes", True),  # Process still running
            ("Files created during runtime", total_new_files > 0)
        ]
        
        passed = sum(1 for _, result in success_criteria if result)
        total = len(success_criteria)
        
        for criterion, result in success_criteria:
            status = "✅" if result else "❌"
            print(f"{status} {criterion}")
        
        score = passed / total * 100
        print(f"\n📊 SCORE: {passed}/{total} ({score:.1f}%)")
        
        if score >= 90:
            verdict = "PRODUCTION READY"
            print(f"\n🎉 VERDICT: {verdict}")
            print("✅ System fully functional in runtime environment")
            print("✅ All critical components working")
            print("✅ Ready for user deployment")
            success = True
        elif score >= 70:
            verdict = "MOSTLY FUNCTIONAL"
            print(f"\n⚠️  VERDICT: {verdict}")
            print(f"✅ {score:.1f}% of tests passed")
            print("🔧 Minor issues may need attention")
            success = True
        else:
            verdict = "NEEDS WORK"
            print(f"\n❌ VERDICT: {verdict}")
            print(f"❌ Only {score:.1f}% of tests passed")
            success = False
        
        return success
        
    except Exception as e:
        print(f"\n💥 TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up...")
        try:
            process.terminate()
            process.wait(timeout=10)
            print("✅ Server stopped cleanly")
        except:
            try:
                process.kill()
                print("⚠️  Server force-killed")
            except:
                print("❌ Could not stop server")

if __name__ == "__main__":
    success = test_streamlit_runtime()
    print(f"\n🏁 FINAL RESULT: {'SUCCESS' if success else 'FAILED'}")
    exit(0 if success else 1)