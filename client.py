
#!/usr/bin/env python3
"""FAST MCP client: binary, length-prefixed JSON over TCP."""

import socket
import json
import sys
import struct

def send_request(host: str, port: int, req: dict) -> dict:
    s = socket.create_connection((host, port))
    with s:
        f = s.makefile(mode="rwb")
        payload = json.dumps(req).encode()
        f.write(struct.pack('>I', len(payload)))
        f.write(payload)
        f.flush()
        len_bytes = f.read(4)
        if not len_bytes or len(len_bytes) < 4:
            raise RuntimeError("No response length prefix")
        msg_len = struct.unpack('>I', len_bytes)[0]
        resp_bytes = f.read(msg_len)
        if not resp_bytes or len(resp_bytes) < msg_len:
            raise RuntimeError("Incomplete response")
        return json.loads(resp_bytes.decode())

def main():
    # Generate architecture request (requires Azure OpenAI credentials)
    req = {
        "id": 4,
        "type": "request",
        "method": "generate_architecture",
        "params": {
            "prompt": "Design a scalable web application on Azure with a load balancer, app service, and Azure SQL database."
        }
    }
    print("Generate Architecture Request:", req)
    try:
        #this is for local
        host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
        resp = send_request(host, port, req)
        print("Generate Architecture Response:", resp)
    except Exception as e:
        print("Error during architecture generation:", e)
    

    # Echo request
    req = {"id": 1, "type": "request", "method": "echo", "params": {"message": "Hello FAST MCP"}}
    print("Echo Request:", req)
    resp = send_request(host, port, req)
    print("Echo Response:", resp)

    # Add request (commented out)
    # req = {"id": 2, "type": "request", "method": "add", "params": {"a": 20, "b": 5}}
    # print("Add Request:", req)
    # resp = send_request(host, port, req)
    # print("Add Response:", resp)

    # Subtract request (commented out)
    # req = {"id": 3, "type": "request", "method": "subtract", "params": {"a": 10, "b": 5}}
    # print("Subtract Request:", req)
    # resp = send_request(host, port, req)
    # print("Subtract Response:", resp)

if __name__ == "__main__":
    main()
