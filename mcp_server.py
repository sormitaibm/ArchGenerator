
#!/usr/bin/env python3
"""
FastMCP server for architecture generation with GitHub Copilot agent integration.
"""

import datetime
import sys
import argparse
try:
    import openai
except ImportError:
    openai = None

try:
    import config
except ImportError:
    config = None

from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Architecture Generator")

@mcp.tool()
def echo(message: str) -> dict:
    """Echo back the provided message."""
    return {"echo": message}

@mcp.tool()
def add(a: float, b: float) -> dict:
    """Add two numbers and return the sum."""
    return {"sum": a + b}

@mcp.tool()
def subtract(a: float, b: float) -> dict:
    """Subtract two numbers and return the difference."""
    return {"difference": a - b}

@mcp.tool()
def generate_architecture(prompt: str) -> dict:
    """Generate Azure architecture diagram in Mermaid JS notation."""
    if not prompt:
        raise ValueError("Missing prompt for architecture generation")
    if openai is None:
        raise ImportError("openai package not installed")
    
    # Azure OpenAI config: get from config.py
    api_key = getattr(config, "API_KEY", None)
    endpoint = getattr(config, "API_BASE", None)
    api_version = getattr(config, "API_VERSION", "2023-05-15")
    deployment = getattr(config, "DEPLOYMENT", None)
    
    if not api_key or not endpoint or not deployment:
        raise ValueError("Azure OpenAI credentials not set in config.py")
    
    openai.api_type = "azure"
    openai.api_key = api_key
    openai.api_base = endpoint
    openai.api_version = api_version
    
    # Compose the prompt for Mermaid JS diagram
    system_prompt = "You are an expert Azure architect. Given a user prompt, generate an Azure architecture diagram in Mermaid JS notation. Only output the diagram code."
    user_prompt = prompt
    
    try:
        response = openai.ChatCompletion.create(
            engine=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )
        mermaid_code = response["choices"][0]["message"]["content"]
        return {"mermaid": mermaid_code}
    except Exception as e:
        raise ValueError(f"Azure OpenAI error: {e}")

@mcp.tool()
def get_current_time() -> dict:
    """Get the current UTC time in ISO format."""
    return {"time": datetime.datetime.utcnow().isoformat() + "Z"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='FastMCP Architecture Generator Server')
    parser.add_argument('--mode', choices=['stdio', 'http'], default='stdio',
                        help='Server mode: stdio for GitHub Copilot, http for remote access')
    parser.add_argument('--host', default='0.0.0.0', help='HTTP host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='HTTP port (default: 8000)')
    
    args = parser.parse_args()
    
    if args.mode == 'http':
        # Run in HTTP mode for remote connectivity
        print(f"Starting MCP server in HTTP mode on {args.host}:{args.port}")
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        # Run in STDIO mode for GitHub Copilot
        print("Starting MCP server in STDIO mode for GitHub Copilot", file=sys.stderr)
        mcp.run()
