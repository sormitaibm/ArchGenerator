from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback
import asyncio
import datetime
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    import openai
except ImportError:
    openai = None

try:
    import config
except ImportError:
    config = None

# Import the MCP instance from mcp_server
from mcp_server import mcp

app = FastAPI(title="MCP Architecture Generator Web API", 
              description="HTTP wrapper for MCP tools")

# FastMCP-style tool implementations (direct functions for web API)
def echo(message: str) -> dict:
    """Echo back the provided message."""
    return {"echo": message}

def add(a: float, b: float) -> dict:
    """Add two numbers and return the sum."""
    return {"sum": a + b}

def subtract(a: float, b: float) -> dict:
    """Subtract two numbers and return the difference."""
    return {"difference": a - b}

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

def get_current_time() -> dict:
    """Get the current UTC time in ISO format."""
    return {"time": datetime.datetime.utcnow().isoformat() + "Z"}

# Tool dispatch mapping
TOOLS = {
    "echo": echo,
    "add": add,
    "subtract": subtract,
    "generate_architecture": generate_architecture,
    "time": get_current_time,
    "get_current_time": get_current_time
}

def handle_tool_call(method: str, params: dict) -> dict:
    """Handle FastMCP-style tool calls."""
    if method not in TOOLS:
        raise ValueError(f"Unknown tool: {method}")
    
    tool_func = TOOLS[method]
    
    # Extract parameters based on tool requirements
    if method == "echo":
        return tool_func(params.get("message", ""))
    elif method in ["add", "subtract"]:
        return tool_func(params.get("a", 0), params.get("b", 0))
    elif method == "generate_architecture":
        return tool_func(params.get("prompt", ""))
    elif method in ["time", "get_current_time"]:
        return tool_func()
    else:
        raise ValueError(f"Tool {method} not configured")

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Architecture Generator", "timestamp": datetime.datetime.utcnow().isoformat()}

# Individual tool endpoints
@app.post("/echo")
async def echo_endpoint(request: Request):
    data = await request.json()
    message = data.get("message", "")
    return echo(message)

@app.post("/add") 
async def add_endpoint(request: Request):
    data = await request.json()
    a = data.get("a", 0)
    b = data.get("b", 0)
    return add(a, b)

@app.post("/subtract")
async def subtract_endpoint(request: Request):
    data = await request.json()
    a = data.get("a", 0) 
    b = data.get("b", 0)
    return subtract(a, b)

@app.get("/time")
async def time_endpoint():
    return get_current_time()

@app.post("/generate_architecture")
async def generate_architecture_endpoint(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, generate_architecture, prompt)
    return result

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    import time
    print("/mcp request received")
    start = time.time()
    try:
        req_json = await request.json()
        result = None
        error = None
        
        try:
            method = req_json.get("method")
            params = req_json.get("params", {})
            
            # Handle async execution for generate_architecture
            if method == "generate_architecture":
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: handle_tool_call(method, params))
            else:
                result = handle_tool_call(method, params)
                
        except Exception as e:
            error = str(e)
            traceback.print_exc()
        
        # Create FastMCP-style response
        resp = {
            "id": req_json.get("id"),
            "type": "response"
        }
        if error is not None:
            resp["error"] = {"message": error}
        else:
            resp["result"] = result
            
        print(f"/mcp request finished in {time.time()-start:.2f}s")
        return JSONResponse(content=resp)
    except Exception as e:
        print(f"/mcp error: {e}")
        return JSONResponse(content={"type": "error", "message": str(e)}, status_code=400)

# For local testing only
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
