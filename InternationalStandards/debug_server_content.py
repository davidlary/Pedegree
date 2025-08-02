#!/usr/bin/env python3
"""Debug server content to fix Phase 2 failure"""

import subprocess
import time
import requests

def debug_server_content():
    print("🔍 DEBUGGING SERVER CONTENT - PHASE 2 FIX")
    print("=" * 50)
    
    # Start server
    server_process = subprocess.Popen([
        "streamlit", "run", "GetInternationalStandards.py",
        "--server.port=8507", 
        "--server.headless=true",
        "--server.enableCORS=false"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    server_url = "http://localhost:8507"
    
    # Wait for server
    print("⏳ Waiting for server...")
    for i in range(60):
        try:
            response = requests.get(server_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Server ready after {i} seconds")
                break
        except:
            pass
        time.sleep(1)
    else:
        print("❌ Server failed to start")
        server_process.terminate()
        return
    
    # Analyze content
    content = response.text
    print(f"📊 Content length: {len(content)} bytes")
    print(f"📊 Content type: {response.headers.get('content-type', 'unknown')}")
    
    # Check for elements
    elements_to_check = ['Streamlit', 'javascript', 'script', 'root', '<!DOCTYPE html>', '<div id="root">']
    
    print(f"\n🔍 Element analysis:")
    for element in elements_to_check:
        found = element in content
        case_insensitive_found = element.lower() in content.lower()
        print(f"  {element}: {'✅' if found else '❌'} (case-insensitive: {'✅' if case_insensitive_found else '❌'})")
    
    # Show first 500 characters
    print(f"\n📄 First 500 characters of content:")
    print("-" * 50)
    print(content[:500])
    print("-" * 50)
    
    # Show last 200 characters  
    print(f"\n📄 Last 200 characters of content:")
    print("-" * 50)
    print(content[-200:])
    print("-" * 50)
    
    # Look for variations
    streamlit_variations = ['streamlit', 'Streamlit', 'STREAMLIT', 'stLite', 'st-lite']
    print(f"\n🔍 Streamlit variations check:")
    for variation in streamlit_variations:
        found = variation in content
        print(f"  {variation}: {'✅' if found else '❌'}")
    
    server_process.terminate()
    
    # ROOT CAUSE ANALYSIS
    print(f"\n🔧 ROOT CAUSE ANALYSIS:")
    if len(content) < 1000:
        print("❌ Content too short - server may not be fully ready")
    elif '<!DOCTYPE html>' not in content:
        print("❌ Not HTML content - server error")
    elif '<div id="root">' not in content:
        print("❌ Missing React root div - Streamlit not loading")
    elif not any(var in content for var in streamlit_variations):
        print("❌ No Streamlit branding found - may be generic HTML")
    else:
        print("✅ Content structure looks correct")

if __name__ == "__main__":
    debug_server_content()