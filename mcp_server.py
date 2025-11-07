from logging import config as logging_config
import os
import sys
import logging

import openai
import config

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
    
    logger.info("Importing pydantic...")
    import pydantic
    
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

if __name__ == "__main__":
    try:
        logger.info("Starting MCP server on host 0.0.0.0:8000")
        mcp.run(transport="http", host='0.0.0.0', port=8000)
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
