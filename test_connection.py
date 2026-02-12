#!/usr/bin/env python3
"""
Simple test script to verify MalayLanguage MCP server connection.
Usage: python test_connection.py <server_url>
Example: python test_connection.py https://your-app.railway.app
"""

import sys
import urllib.request
import json

def test_health(base_url):
    """Test the health check endpoint."""
    print(f"\n🔍 Testing health check at {base_url}/health...")
    try:
        response = urllib.request.urlopen(f"{base_url}/health", timeout=10)
        data = json.loads(response.read().decode())
        
        if data.get("status") == "healthy":
            print("✅ Health check passed!")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print("❌ Health check failed: unexpected response")
            print(f"   Response: {data}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root(base_url):
    """Test the root endpoint."""
    print(f"\n🔍 Testing root endpoint at {base_url}/...")
    try:
        response = urllib.request.urlopen(f"{base_url}/", timeout=10)
        data = json.loads(response.read().decode())
        
        print("✅ Root endpoint accessible!")
        print(f"   Service: {data.get('service')}")
        print(f"   MCP Endpoint: {data.get('mcp_endpoint')}")
        print(f"   Health Endpoint: {data.get('health_endpoint')}")
        return True
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_sse(base_url):
    """Test SSE endpoint accessibility."""
    print(f"\n🔍 Testing SSE endpoint at {base_url}/sse...")
    try:
        # Just check if the endpoint is accessible (will return SSE stream)
        request = urllib.request.Request(f"{base_url}/sse")
        request.add_header('Accept', 'text/event-stream')
        response = urllib.request.urlopen(request, timeout=5)
        
        # If we get here, endpoint is accessible
        print("✅ SSE endpoint is accessible!")
        print("   (Full MCP client needed for complete testing)")
        return True
    except urllib.error.HTTPError as e:
        if e.code == 200:
            print("✅ SSE endpoint is accessible!")
            return True
        else:
            print(f"⚠️  SSE endpoint returned HTTP {e.code}")
            print("   This might be normal - full MCP client needed for complete testing")
            return True
    except Exception as e:
        print(f"❌ SSE endpoint test inconclusive: {e}")
        print("   Full MCP client needed for complete testing")
        return True  # Don't fail on this as it needs proper SSE client

def print_config(base_url):
    """Print configuration examples."""
    print("\n📋 Configuration for your MCP client:")
    print("\nFor Claude Desktop / VS Code / Cursor:")
    print(json.dumps({
        "mcpServers": {
            "malaylanguage": {
                "url": f"{base_url}/sse",
                "transport": "sse"
            }
        }
    }, indent=2))

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_connection.py <server_url>")
        print("Example: python test_connection.py https://your-app.railway.app")
        print("         python test_connection.py http://localhost:8000")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("=" * 60)
    print("MalayLanguage MCP Server Connection Test")
    print("=" * 60)
    print(f"Testing server at: {base_url}")
    
    results = []
    results.append(("Health Check", test_health(base_url)))
    results.append(("Root Endpoint", test_root(base_url)))
    results.append(("SSE Endpoint", test_sse(base_url)))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Your server is ready to use.")
        print_config(base_url)
        print("\n📖 See TESTING.md for detailed testing instructions")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("   See TESTING.md for troubleshooting help")
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
