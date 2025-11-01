
#!/usr/bin/env python3
"""
FAST MCP-style server: binary, length-prefixed JSON requests and responses.

Protocol:
- Each message is a 4-byte big-endian length prefix, followed by a UTF-8 JSON payload.
- Request: {"id": <int>, "type":"request", "method":"echo"|"add"|"time", "params": {...}}
- Response: {"id": <same>, "type":"response", "result": {...}} or error with "error": {"message":...}
"""


import json
import socket
import threading
import datetime
import sys
#import os
import struct
try:
    import openai
except ImportError:
    openai = None

try:
    import config
except ImportError:
    config = None

def handle_message(msg: dict) -> dict:
    """Handle a parsed JSON request (as dict) and return a result dict."""
    if not isinstance(msg, dict):
        raise ValueError("message must be an object")
    method = msg.get("method")
    params = msg.get("params", {}) or {}
    if method == "echo":
        return {"echo": params.get("message")}
    elif method == "add":
        a = params.get("a", 0)
        b = params.get("b", 0)
        try:
            return {"sum": a + b}
        except Exception:
            return {"sum": float(a) + float(b)}
    elif method == "subtract":
        a = params.get("a", 0)
        b = params.get("b", 0)
        try:
            return {"difference": a - b}
        except Exception:
            return {"difference": float(a) - float(b)}
    elif method == "generate_architecture":
        prompt = params.get("prompt", "")
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
    elif method == "time":
        return {"time": datetime.datetime.utcnow().isoformat() + "Z"}
    else:
        raise ValueError(f"unknown method: {method}")

def make_response(req: dict, result: dict = None, error: str = None) -> dict:
    resp = {"id": req.get("id")}
    resp["type"] = "response"
    if error is not None:
        resp["error"] = {"message": str(error)}
    else:
        resp["result"] = result
    return resp

def read_frame(f) -> bytes:
    """Read a FAST MCP frame: 4-byte length prefix, then payload."""
    len_bytes = f.read(4)
    if not len_bytes or len(len_bytes) < 4:
        return None
    msg_len = struct.unpack('>I', len_bytes)[0]
    payload = f.read(msg_len)
    if not payload or len(payload) < msg_len:
        return None
    return payload

def write_frame(f, payload: bytes):
    """Write a FAST MCP frame: 4-byte length prefix, then payload."""
    msg_len = len(payload)
    f.write(struct.pack('>I', msg_len))
    f.write(payload)
    f.flush()

def handle_connection(conn: socket.socket, addr):
    import traceback
    with conn:
        f = conn.makefile(mode="rwb")
        while True:
            payload = read_frame(f)
            if payload is None:
                break
            try:
                req = json.loads(payload.decode())
                try:
                    res = handle_message(req)
                    resp = make_response(req, result=res)
                except Exception as e:
                    print("[SERVER ERROR] Exception in handle_message:")
                    traceback.print_exc()
                    resp = make_response(req, error=str(e))
            except Exception as e:
                print("[SERVER ERROR] Exception in connection handler:")
                traceback.print_exc()
                resp = {"type": "error", "message": str(e)}
            out = json.dumps(resp).encode()
            write_frame(f, out)

def run_server(host: str = "127.0.0.1", port: int = 5000):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(5)
    print(f"Listening on {host}:{port} (FAST MCP)")
    try:
        while True:
            conn, addr = srv.accept()
            t = threading.Thread(target=handle_connection, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("Shutting down")
    finally:
        srv.close()

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5000
    run_server(host, port)
