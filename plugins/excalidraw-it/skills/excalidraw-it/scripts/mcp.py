"""Call a tool of the Excalidraw+ MCP over HTTP, so that its payload and its answer stay out of the context.

The server is stateless: each call is one JSON-RPC request carrying the API key.
"""
import json
import sys
import urllib.error
import urllib.request

from key import api_key

URL = "https://api.excalidraw.com/api/v1/mcp"


def call(tool, arguments):
    """Return the text the tool answers, parsed as JSON when it is JSON."""
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": tool, "arguments": arguments}}
    request = urllib.request.Request(URL, json.dumps(body).encode(), {
        "Authorization": f"Bearer {api_key()}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    })
    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read().decode()
            if response.headers.get_content_type() == "text/event-stream":
                raw = [line[5:] for line in raw.splitlines() if line.startswith("data:")][-1]
    except urllib.error.HTTPError as error:
        sys.exit(f"{tool} -> {error.code} {error.read().decode()}")
    answer = json.loads(raw)
    if "error" in answer:
        sys.exit(f"{tool} -> {answer['error']}")
    text = "".join(part.get("text", "") for part in answer["result"]["content"])
    if answer["result"].get("isError"):
        sys.exit(f"{tool} -> {text}")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text
