import sys
import os
import asyncio
import json
import urllib.request

# Configuration: prefer env var but keep the default used previously
AZURE_APP_SERVICE_URL = os.environ.get(
    "AZURE_APP_SERVICE_URL",
    "https://archgenmcpserver-c0hycpg7ddebcqdf.centralus-01.azurewebsites.net/mcp/",
)

DEFAULT_PROMPT = (
    "Design a scalable web application on Azure with a load balancer, "
    "app service, and Azure SQL database."
)


async def call_generate_architecture(prompt: str):
    """Call the remote MCP tool 'generate_architecture'.

    Implementation details:
    - Try to use the `fastmcp` client if it's installed (preferred).
    - Fallback to a plain HTTP POST (JSON-RPC style) using the standard
      library if `fastmcp` isn't available or fails.

    This keeps the client usable in environments where `fastmcp` is not
    installed (e.g., CI) while still supporting the streaming client when
    available.
    """

    print(f"Connecting to MCP server at: {AZURE_APP_SERVICE_URL}")

    # First attempt: use fastmcp (if available)
    try:
        from fastmcp import Client  # type: ignore
        from fastmcp.client.transports import StreamableHttpTransport  # type: ignore

        client = Client(StreamableHttpTransport(AZURE_APP_SERVICE_URL))
        params = {"prompt": prompt}
        print(f"Calling tool 'generate_architecture' with params: {params}")

        resp = await client.tools.generate_architecture(**params)

        # Handle streaming vs single response
        if hasattr(resp, "__aiter__"):
            print("Streaming response:")
            async for part in resp:
                print(part)
        else:
            print("Generate Architecture Response:")
            print(resp)

        return
    except Exception as e:  # fastmcp not available or call failed
        print("fastmcp client not usable or call failed, falling back to HTTP POST.")
        print("fastmcp error:", e)

    # Fallback: plain HTTP POST (JSON-RPC style). Use urllib to avoid new deps.
    try:
        
        rpc_req = {
            "id": 1,
            "type": "request",
            "method": "generate_architecture",
            "params": {"prompt": prompt},
        }
        data = json.dumps(rpc_req).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(AZURE_APP_SERVICE_URL, data=data, headers=headers)

        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            try:
                j = json.loads(body)
            except Exception:
                print("Non-JSON response from server:")
                print(body)
                return

            # Server expected to return a JSON-RPC response with either 'result' or 'error'
            if j.get("type") == "response":
                if "result" in j:
                    print("Generate Architecture Response:")
                    print(j["result"])
                else:
                    print("Server returned error:", j.get("error"))
            else:
                # Some deployments may return the direct tool result
                print("Response:")
                print(j)
    except Exception as e:
        print("HTTP fallback failed:", e)


if __name__ == "__main__":
    # Accept prompt via CLI or fall back to default
    prompt = DEFAULT_PROMPT
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])

    # Run the coroutine
    asyncio.run(call_generate_architecture(prompt))