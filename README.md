# Sample FAST MCP-style Python Program

This repository contains a minimal example of a "Model Context Protocol" program using the FAST MCP protocol (binary, length-prefixed JSON) in Python.

Files:
- `mcp_server.py` — TCP server using FAST MCP (4-byte length prefix, then UTF-8 JSON).
- `client.py` — client using FAST MCP to send requests and print responses.
- `tests/test_mcp.py` — unit tests for the server handler.
- `requirements.txt` — no external dependencies required.


FAST MCP Protocol:
- Each message is a 4-byte big-endian length prefix, followed by a UTF-8 JSON payload.
- Request: `{ "id": <int>, "type": "request", "method": "echo"|"add"|"subtract"|"time"|"generate_architecture", "params": {...} }`
- Response: `{ "id": <same>, "type": "response", "result": {...} }` or error with `"error": {"message":...}`

Example methods:
- `echo`: returns the message in `result.echo`.
- `add`: returns the sum in `result.sum`.
- `subtract`: returns the difference in `result.difference`.
- `time`: returns the current UTC time in `result.time`.
- `generate_architecture`: returns a Mermaid JS diagram in `result.mermaid` (requires Azure OpenAI credentials).

## Azure OpenAI Setup

To use the `generate_architecture` method, set these environment variables before starting the server:

- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint (e.g. https://<your-resource>.openai.azure.com/)
- `AZURE_OPENAI_DEPLOYMENT`: Your deployment name (e.g. "gpt-4")

Install dependencies:
```powershell
pip install -r requirements.txt
```

## Example: Generate Azure Architecture Diagram

The client sends a request like:
```json
{
	"id": 4,
	"type": "request",
	"method": "generate_architecture",
	"params": {
		"prompt": "Design a scalable web application on Azure with a load balancer, app service, and Azure SQL database."
	}
}
```
The server responds with:
```json
{
	"id": 4,
	"type": "response",
	"result": {
		"mermaid": "graph TD\n..."
	}
}
```

Usage (PowerShell):

```powershell
# Start the server (foreground)
python .\mcp_server.py 127.0.0.1 5000

# In another terminal, run the client
python .\client.py 127.0.0.1 5000
```

Run tests:

```powershell
python -m unittest discover -v
```

Notes:
- This is an example only — the protocol is deliberately simple to demonstrate the FAST MCP pattern.
