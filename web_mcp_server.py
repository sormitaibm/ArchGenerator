from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import mcp_server
import traceback

app = FastAPI()

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    try:
        req_json = await request.json()
        result = None
        error = None
        try:
            result = mcp_server.handle_message(req_json)
        except Exception as e:
            error = str(e)
            traceback.print_exc()
        resp = mcp_server.make_response(req_json, result=result, error=error)
        return JSONResponse(content=resp)
    except Exception as e:
        return JSONResponse(content={"type": "error", "message": str(e)}, status_code=400)

# For local testing only
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
