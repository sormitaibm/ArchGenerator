
#!/usr/bin/env python3
"""FastMCP client: Test client for FastMCP server tools via HTTP API."""

import json
import sys
import urllib.request
import urllib.parse

def send_http_request(url: str, req: dict) -> dict:
    """Send request to FastMCP web server via HTTP."""
    try:
        data = json.dumps(req).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        
        request = urllib.request.Request(url, data=data, headers=headers)
        
        with urllib.request.urlopen(request, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
            
    except Exception as e:
        print(f"HTTP request failed: {e}")
        return {"type": "error", "message": str(e)}

def test_fastmcp_tools(base_url: str = "http://localhost:8000"):
    """Test all FastMCP tools via HTTP endpoint."""
    mcp_url = f"{base_url}/mcp"
    
    print("Testing FastMCP Tools via HTTP API")
    print("=" * 40)
    
    # Test 1: Echo
    echo_req = {
        "id": 1,
        "type": "request", 
        "method": "echo",
        "params": {"message": "Hello FastMCP!"}
    }
    
    print(f"\n1. Testing Echo Tool:")
    print(f"   Request: {echo_req}")
    echo_resp = send_http_request(mcp_url, echo_req)
    print(f"   Response: {echo_resp}")
    
    # Test 2: Add
    add_req = {
        "id": 2,
        "type": "request",
        "method": "add", 
        "params": {"a": 15, "b": 25}
    }
    
    print(f"\n2. Testing Add Tool:")
    print(f"   Request: {add_req}")
    add_resp = send_http_request(mcp_url, add_req)
    print(f"   Response: {add_resp}")
    
    # Test 3: Subtract
    sub_req = {
        "id": 3,
        "type": "request",
        "method": "subtract",
        "params": {"a": 50, "b": 20}
    }
    
    print(f"\n3. Testing Subtract Tool:")
    print(f"   Request: {sub_req}")
    sub_resp = send_http_request(mcp_url, sub_req)
    print(f"   Response: {sub_resp}")
    
    # Test 4: Current Time
    time_req = {
        "id": 4,
        "type": "request",
        "method": "get_current_time",
        "params": {}
    }
    
    print(f"\n4. Testing Time Tool:")
    print(f"   Request: {time_req}")
    time_resp = send_http_request(mcp_url, time_req)
    print(f"   Response: {time_resp}")
    
    return [echo_resp, add_resp, sub_resp, time_resp]

def main():
    """Main function to test FastMCP tools."""
    
    # Default to local web server
    base_url = "http://localhost:8000"
    
    # Allow override via command line
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"Testing FastMCP server at: {base_url}")
    
    # Run all tool tests
    responses = test_fastmcp_tools(base_url)
    
    # Test architecture generation (requires Azure OpenAI credentials)
    print(f"\n5. Testing Architecture Generation:")
    arch_req = {
        "id": 5,
        "type": "request",
        "method": "generate_architecture", 
        "params": {
            "prompt": "Design a scalable web application on Azure with a load balancer, app service, and Azure SQL database."
        }
    }
    
    print(f"   Request: {arch_req}")
    try:
        mcp_url = f"{base_url}/mcp"
        arch_resp = send_http_request(mcp_url, arch_req)
        print(f"   Response: {arch_resp}")
        
        # If successful, show mermaid code
        if arch_resp.get("result") and "mermaid" in arch_resp["result"]:
            print(f"\n   Generated Mermaid Diagram:")
            print(f"   {arch_resp['result']['mermaid']}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print(f"\n✅ FastMCP client testing complete!")
    print(f"   Use 'python client.py [base_url]' to test different servers")
    print(f"   Default: python client.py (tests http://localhost:8000)")
    print(f"   Remote:  python client.py https://your-server.com")

if __name__ == "__main__":
    main()
