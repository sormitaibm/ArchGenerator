from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import mcp_server
import traceback

app = FastAPI()

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
            # If OpenAI supports async, use await. Otherwise, run in thread.
            if req_json.get("method") == "generate_architecture":
                import openai
                # Patch: set a longer timeout for OpenAI if possible
                # openai.ChatCompletion.create does not have a timeout param, so use default
                # If you use httpx as transport, you can set timeout
                # Otherwise, run in a thread to avoid blocking event loop
                import asyncio
                loop = asyncio.get_event_loop()
                def blocking_call():
                    return mcp_server.handle_message(req_json)
                result = await loop.run_in_executor(None, blocking_call)
            else:
                result = mcp_server.handle_message(req_json)
        except Exception as e:
            error = str(e)
            traceback.print_exc()
        resp = mcp_server.make_response(req_json, result=result, error=error)
        print(f"/mcp request finished in {time.time()-start:.2f}s")
        return JSONResponse(content=resp)
    except Exception as e:
        print(f"/mcp error: {e}")
        return JSONResponse(content={"type": "error", "message": str(e)}, status_code=400)

# For local testing only
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
