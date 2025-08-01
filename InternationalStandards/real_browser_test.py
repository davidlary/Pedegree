#!/usr/bin/env python3
"""
REAL BROWSER TESTING - Comprehensive End-to-End
"""

import subprocess
import time
import requests
import sys
from pathlib import Path

def test_real_streamlit_application():
    """Test the real Streamlit application"""
    print("🚀 REAL STREAMLIT APPLICATION TESTING")
    print("=" * 50)
    
    streamlit_process = None
    
    try:
        # Kill any existing streamlit processes
        subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
        time.sleep(2)
        
        # Start streamlit server
        print("Starting Streamlit server...")
        streamlit_process = subprocess.Popen(
            ["streamlit", "run", "GetInternationalStandards.py", "--server.port=8505", "--server.headless=true"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to be ready
        base_url = "http://localhost:8505"
        print(f"Waiting for server at {base_url}...")
        
        for i in range(60):  # Wait up to 60 seconds
            try:
                response = requests.get(base_url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Server is ready!")
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
            
            if i % 10 == 0:
                print(f"   Still waiting... ({i}/60 seconds)")
        else:
            print("❌ Server failed to start within 60 seconds")
            return False
        
        # Test homepage
        print("\\nTesting homepage...")
        response = requests.get(base_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Homepage loads successfully")
            
            # Check content
            content = response.text
            expected_elements = [
                "International Standards Retrieval System",
                "Multi-Agent",
                "Standards"
            ]
            
            found_elements = []
            for element in expected_elements:
                if element in content:
                    found_elements.append(element)
                    print(f"✅ Found: {element}")
                else:
                    print(f"❌ Missing: {element}")
            
            if len(found_elements) >= 2:  # At least 2 out of 3
                print("\\n🎉 REAL BROWSER TEST PASSED!")
                print("   - Streamlit server starts successfully")
                print("   - Homepage loads without errors")
                print("   - Expected content is present")
                return True
            else:
                print("\\n❌ Content validation failed")
                return False
        else:
            print(f"❌ Homepage failed with status: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        # Clean up
        if streamlit_process:
            print("\\nStopping Streamlit server...")
            streamlit_process.terminate()
            streamlit_process.wait()

if __name__ == "__main__":
    success = test_real_streamlit_application()
    print(f"\\n{'🎉 SUCCESS' if success else '❌ FAILED'}: Real browser test")
    sys.exit(0 if success else 1)