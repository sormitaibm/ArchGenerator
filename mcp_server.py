import datetime
import sys
import argparse

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

if __name__ == "__main__":
    mcp.run(transport="http", host='0.0.0.0', port=8000)