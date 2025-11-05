import os
import sys
import logging

# Configure logging for App Service
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

# Print Python environment info for debugging
logger.info(f"Python version: {sys.version}")
logger.info(f"Python executable: {sys.executable}")

try:
    # Import dependencies step by step for better error tracking
    logger.info("Importing typing_extensions...")
    import typing_extensions
    logger.info(f"typing_extensions {typing_extensions.__version__} loaded from {typing_extensions.__file__}")
    
    logger.info("Importing pydantic...")
    import pydantic
    logger.info(f"pydantic {pydantic.__version__} loaded successfully")
    
    logger.info("Importing FastMCP...")
    from fastmcp import FastMCP
    logger.info("FastMCP imported successfully")
    
except Exception as e:
    logger.error(f"Import failed: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)

# Initialize FastMCP server
logger.info("Initializing FastMCP server...")
mcp = FastMCP("Architecture Generator")
logger.info("FastMCP server initialized successfully")

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
    try:
        logger.info("Starting MCP server on host 0.0.0.0:8000")
        mcp.run(transport="http", host='0.0.0.0', port=8000)
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
