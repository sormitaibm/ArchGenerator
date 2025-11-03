import sys
import os
import asyncio
import json
import urllib.request

# Configuration: prefer env var but keep the default used previously
AZURE_APP_SERVICE_URL = os.environ.get(
    "AZURE_APP_SERVICE_URL",
    "https://archgenmcpserver-c0hycpg7ddebcqdf.centralus-01.azurewebsites.net/mcp",
)

DEFAULT_PROMPT = (
    "Design a scalable web application on Azure with a load balancer, "
    "app service, and Azure SQL database."
)


async def call_fastmcp_tool(tool_name: str, params: dict):
    """Call any FastMCP tool via HTTP POST."""
    print(f"Connecting to FastMCP server at: {AZURE_APP_SERVICE_URL}")
    try:
        rpc_req = {
            "id": 1,
            "type": "request",
            "method": tool_name,
            "params": params,
        }
        data = json.dumps(rpc_req).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(AZURE_APP_SERVICE_URL, data=data, headers=headers)

        with urllib.request.urlopen(req, timeout=60) as resp:  # Increased timeout for AI calls
            body = resp.read().decode("utf-8")
            try:
                j = json.loads(body)
            except Exception:
                print("Non-JSON response from server:")
                print(body)
                return None

            # FastMCP server returns JSON-RPC response with either 'result' or 'error'
            if j.get("type") == "response":
                if "result" in j:
                    print(f"✅ {tool_name.title()} Tool Response:")
                    result = j["result"]
                    
                    # Pretty print different result types
                    if tool_name == "generate_architecture" and "mermaid" in result:
                        print("Generated Mermaid Diagram:")
                        print(result["mermaid"])
                    elif tool_name == "echo" and "echo" in result:
                        print(f"Echo: {result['echo']}")
                    elif tool_name in ["add", "subtract"] and ("sum" in result or "difference" in result):
                        key = "sum" if "sum" in result else "difference"
                        print(f"Result: {result[key]}")
                    elif tool_name == "get_current_time" and "time" in result:
                        print(f"Current time: {result['time']}")
                    else:
                        print(result)
                    
                    return result
                else:
                    print("❌ Server returned error:", j.get("error"))
                    return None
            else:
                # Fallback for direct tool result
                print("Response:")
                print(j)
                return j
    except Exception as e:
        print(f"❌ HTTP POST failed: {e}")
        return None

async def call_generate_architecture(prompt: str):
    """Call the FastMCP 'generate_architecture' tool via HTTP POST."""
    return await call_fastmcp_tool("generate_architecture", {"prompt": prompt})

async def test_all_tools():
    """Test all available FastMCP tools."""
    print("🧪 Testing all FastMCP tools...")
    print("=" * 50)
    
    # Test 1: Echo
    print("\n1. Testing Echo Tool:")
    await call_fastmcp_tool("echo", {"message": "Hello from FastMCP client!"})
    
    # Test 2: Add
    print("\n2. Testing Add Tool:")
    await call_fastmcp_tool("add", {"a": 15, "b": 27})
    
    # Test 3: Subtract  
    print("\n3. Testing Subtract Tool:")
    await call_fastmcp_tool("subtract", {"a": 100, "b": 25})
    
    # Test 4: Current Time
    print("\n4. Testing Current Time Tool:")
    await call_fastmcp_tool("get_current_time", {})
    
    print(f"\n🎉 All FastMCP tools tested!")


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ["--test", "-t", "test"]:
            # Test all tools
            asyncio.run(test_all_tools())
        elif sys.argv[1].lower() in ["--help", "-h", "help"]:
            print("FastMCP Client Usage:")
            print("  python appServiceMCPClient.py [prompt]           # Generate architecture")  
            print("  python appServiceMCPClient.py --test             # Test all tools")
            print("  python appServiceMCPClient.py --help             # Show this help")
            print(f"\nServer URL: {AZURE_APP_SERVICE_URL}")
        else:
            # Custom prompt for architecture generation
            prompt = " ".join(sys.argv[1:])
            print(f"🏗️  Generating architecture for: {prompt}")
            asyncio.run(call_generate_architecture(prompt))
    else:
        # Default: generate architecture with default prompt
        print(f"🏗️  Generating architecture with default prompt...")
        print(f"Prompt: {DEFAULT_PROMPT}")
        asyncio.run(call_generate_architecture(DEFAULT_PROMPT))